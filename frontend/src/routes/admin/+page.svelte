<script>
	import Header from '$lib/components/Header.svelte';

	const API_URL = import.meta.env.VITE_API_URL;

	let password = $state('');
	let loggedIn = $state(false);
	let error = $state('');
	let questions = $state([]);

	async function login() {

		error = '';

		try {

			const response = await fetch(
				`${API_URL}/login`,
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

			loggedIn = true;

			await loadQuestions();

		} catch (err) {

			console.error(err);

			error = 'Login failed';
		}
	}

	async function loadQuestions() {

		const response = await fetch(
			`${API_URL}/questions`,
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

			error = 'Failed to load questions';
			return;
		}

		const data = await response.json();

		questions = data.questions;
	}
</script>

<Header />

<div class="container">

	<h1>Hi Oscar!</h1>

	<p>
		Enter your password to view the logs.
	</p>

	{#if !loggedIn}

		<input
			type="password"
			bind:value={password}
			placeholder="Password"
		/>

		<button onclick={login}>
			Log in
		</button>

		{#if error}
			<p>{error}</p>
		{/if}

	{:else}

		<h2>Recent Questions</h2>

		{#each questions as row}

			<details>

				<summary>
					{row[0]}
				</summary>

				<p>
					<strong>IP:</strong><br>
					{row[1]}
				</p>

				<p>
					<strong>Question:</strong><br>
					{row[2]}
				</p>

				<p>
					<strong>Answer:</strong><br>
					{row[3]}
				</p>

			</details>

		{/each}

	{/if}

</div>