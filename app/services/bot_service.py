"""Bot service - Pipecat Gemini Live pipeline."""

import os

from google.genai.types import EndSensitivity, StartSensitivity, ThinkingConfig
from loguru import logger
from pipecat.frames.frames import LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import parse_telephony_websocket
from pipecat.serializers.twilio import TwilioFrameSerializer
from pipecat.services.google.gemini_live.llm import (
    GeminiLiveLLMService,
    GeminiVADParams,
    InputParams,
)
from pipecat.transports.base_transport import BaseTransport
from pipecat.transports.websocket.fastapi import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)

from app.config import get_api_key, get_twilio_config
from app.models.persona import build_system_instruction


async def _run_pipeline(transport: BaseTransport, persona_id: str) -> None:
    """Run the Gemini Live pipeline with the given persona."""
    api_key = get_api_key()
    system_instruction = build_system_instruction(persona_id)

    # Latency optimizations:
    # - thinking_budget=0: disable extended thinking
    # - vad: lower silence_duration_ms = faster turn-end detection; HIGH sensitivity = quicker speech detection
    # - max_tokens: limit response length for voice
    llm = GeminiLiveLLMService(
        api_key=api_key,
        model="gemini-2.5-flash-native-audio-preview-12-2025",
        voice_id="Charon",
        system_instruction=system_instruction,
        params=InputParams(
            thinking=ThinkingConfig(thinking_budget=0),
            vad=GeminiVADParams(
                silence_duration_ms=100,  # Less wait for silence before ending turn (default ~500+)
                prefix_padding_ms=20,
                start_sensitivity=StartSensitivity.START_SENSITIVITY_HIGH,
                end_sensitivity=EndSensitivity.END_SENSITIVITY_HIGH,
            ),
            max_tokens=512,  # Encourage shorter voice responses
        ),
    )

    messages = [
        {
            "role": "user",
            "content": (
                "Greet the caller warmly in one or two short sentences. "
                "Introduce yourself as the assistant and ask how you can help them today."
            ),
        },
    ]

    # user_turn_stop_timeout: lower = faster handoff to LLM after user stops speaking
    context = LLMContext(messages)
    user_aggregator, assistant_aggregator = LLMContextAggregatorPair(
        context,
        user_params=LLMUserAggregatorParams(
            user_turn_stop_timeout=0.5,  # Default 5.0 - reduces latency
        ),
    )

    pipeline = Pipeline(
        [
            transport.input(),
            user_aggregator,
            llm,
            transport.output(),
            assistant_aggregator,
        ]
    )

    enable_metrics = os.getenv("ENABLE_METRICS", "false").lower() == "true"
    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            audio_in_sample_rate=8000,
            audio_out_sample_rate=8000,
            enable_metrics=enable_metrics,
            enable_usage_metrics=enable_metrics,
        ),
    )

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Client connected, starting conversation")
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=False)
    await runner.run(task)


async def run_bot(runner_args: RunnerArguments) -> None:
    """Main bot entry point. Parses Twilio WebSocket and runs the pipeline."""
    transport_type, call_data = await parse_telephony_websocket(runner_args.websocket)
    logger.info(f"Auto-detected transport: {transport_type}")

    if transport_type != "twilio":
        raise ValueError(f"Unsupported transport type: {transport_type}")

    body_data = call_data.get("body", {})
    persona_id = body_data.get("persona_id", "")
    if not persona_id:
        raise ValueError("Missing persona_id in stream parameters")

    logger.info(f"Running bot with persona: {persona_id}")

    account_sid, auth_token, _ = get_twilio_config()

    serializer = TwilioFrameSerializer(
        stream_sid=call_data["stream_id"],
        call_sid=call_data["call_id"],
        account_sid=account_sid,
        auth_token=auth_token,
    )

    transport = FastAPIWebsocketTransport(
        websocket=runner_args.websocket,
        params=FastAPIWebsocketParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            add_wav_header=False,
            serializer=serializer,
        ),
    )

    await _run_pipeline(transport, persona_id)
