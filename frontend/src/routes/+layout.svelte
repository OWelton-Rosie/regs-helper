<script>
	import '../app.css';
	import Footer from '../lib/components/Footer.svelte';

	let { children } = $props();

	import { onMount } from 'svelte';

	const API_URL = import.meta.env.VITE_API_URL;

	let loaded = $state(false);
	let allowed = $state(false);
	let password = $state('');
	let error = $state('');

	onMount(() => {
	allowed = sessionStorage.getItem('beta-access') === 'true';
	loaded = true;
	});

	async function login() {

		error = '';

		try {

			const response = await fetch(
				`${API_URL}/beta-login`,
				{
					method: 'POST',

					headers: {
						'Content-Type': 'application/json'
					},

					body: JSON.stringify({
						password
					})
				}
			);

			if (!response.ok) {

				error = 'Incorrect password';
				return;
			}

			sessionStorage.setItem(
				'beta-access',
				'true'
			);

			allowed = true;

		} catch {

			error = 'Login failed';
		}
	}
</script>

<svelte:head>
	<link rel="icon" href="/assets/favicon.webp" />
</svelte:head>

{#if loaded && !allowed}

	<div class="container">

		<h1>Beta Access Required</h1>

		<p>
			This application is currently in private beta.
		</p>

		<input
			type="password"
			bind:value={password}
			placeholder="Password"
			onkeydown={(e) => e.key === 'Enter' && login()}

		/>

		<button onclick={login}>
			Enter
		</button>

		{#if error}
			<p>{error}</p>
		{/if}

	</div>

{:else if loaded}

	{@render children()}

	<Footer />

{/if}