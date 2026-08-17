<script>
	import { Mic, Square } from '@lucide/svelte';

	let {
		question = $bindable(''),
		loading = false,
		ask
	} = $props();

	let listening = $state(false);
	let voiceSupported = $state(true);
	let voiceError = $state('');

	let recognition;

	function startVoiceInput() {
		voiceError = '';

		const SpeechRecognition =
			window.SpeechRecognition ||
			window.webkitSpeechRecognition;

		if (!SpeechRecognition) {
			voiceSupported = false;
			voiceError =
				'Voice input is not supported by this browser.';
			return;
		}

		if (listening) {
			recognition?.stop();
			return;
		}

		recognition = new SpeechRecognition();

		recognition.lang = 'en-NZ';
		recognition.interimResults = true;
		recognition.continuous = false;

		recognition.onstart = () => {
			listening = true;
		};

		recognition.onresult = (event) => {
			let transcript = '';

			for (
				let i = event.resultIndex;
				i < event.results.length;
				i++
			) {
				transcript +=
					event.results[i][0].transcript;
			}

			if (transcript.trim()) {
				question = transcript.trim();
			}
		};

		recognition.onerror = (event) => {
			console.error(
				'Speech recognition error:',
				event.error
			);

			if (event.error === 'not-allowed') {
				voiceError =
					'Microphone access was denied.';
			} else {
				voiceError =
					'Voice input failed. Please try again.';
			}

			listening = false;
		};

		recognition.onend = () => {
			listening = false;
		};

		recognition.start();
	}

	function handleKeydown(event) {
		if (
			event.key === 'Enter' &&
			(event.metaKey || event.ctrlKey) &&
			!loading &&
			question.trim()
		) {
			event.preventDefault();
			ask();
		}
	}
</script>

<div class="question-input">

	<textarea
		bind:value={question}
		placeholder="Ask a question about the WCA Regulations..."
		onkeydown={handleKeydown}
		disabled={loading}
	></textarea>

	<button
		class="voice-button"
		class:recording={listening}
		type="button"
		onclick={startVoiceInput}
		disabled={loading || !voiceSupported}
		aria-label={
			listening
				? 'Stop voice input'
				: 'Start voice input'
		}
		title={
			listening
				? 'Stop listening'
				: 'Dictate question'
		}
	>
		{#if listening}
			<Square size={18} strokeWidth={2} />
		{:else}
			<Mic size={20} strokeWidth={2} />
		{/if}
	</button>

</div>

<button
	class="ask-button"
	onclick={ask}
	disabled={loading || !question.trim()}
>
	{loading ? 'Searching...' : 'Ask'}
</button>

{#if listening}
	<p class="voice-status">
		Listening...
	</p>
{/if}

{#if voiceError}
	<p class="voice-error">
		{voiceError}
	</p>
{/if}