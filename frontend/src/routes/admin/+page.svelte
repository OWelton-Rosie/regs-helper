<script>
	import Header from '$lib/components/Header.svelte';

	const API_URL = import.meta.env.VITE_API_URL;

	let password = $state('');
	let loggedIn = $state(false);
	let error = $state('');

	let questions = $state([]);
	let reports = $state([]);

	let loading = $state(false);

	async function login() {
		error = '';

		if (!password.trim()) {
			error = 'Please enter the password';
			return;
		}

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

			await loadData();

		} catch (err) {
			console.error(err);

			error = 'Login failed';
		}
	}

	async function loadData() {
		loading = true;
		error = '';

		try {
			const [questionsResponse, reportsResponse] =
				await Promise.all([
					fetch(
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
					),

					fetch(
						`${API_URL}/reports`,
						{
							method: 'POST',

							headers: {
								'Content-Type': 'application/json'
							},

							body: JSON.stringify({
								password
							})
						}
					)
				]);

			if (!questionsResponse.ok) {
				throw new Error('Failed to load questions');
			}

			if (!reportsResponse.ok) {
				throw new Error('Failed to load reports');
			}

			const questionsData =
				await questionsResponse.json();

			const reportsData =
				await reportsResponse.json();

			questions = questionsData.questions;
			reports = reportsData.reports;

		} catch (err) {
			console.error(err);

			error = 'Failed to load admin data';

		} finally {
			loading = false;
		}
	}

	function formatDate(timestamp) {
		const date = new Date(timestamp);

		if (Number.isNaN(date.getTime())) {
			return timestamp;
		}

		return date.toLocaleString();
	}

	function parseSources(sources) {
		if (!sources) {
			return [];
		}

		try {
			return JSON.parse(sources);
		} catch {
			return [];
		}
	}
</script>

<Header />

<div class="container">

	<h1>Hi Oscar!</h1>

	{#if !loggedIn}

		<p>
			Enter the password to view the admin panel.
		</p>

		<input
			type="password"
			bind:value={password}
			placeholder="Password"
			onkeydown={(e) => e.key === 'Enter' && login()}
		/>

		<button
			onclick={login}
			disabled={!password.trim()}
		>
			Log in
		</button>

		{#if error}
			<p class="admin-error">
				{error}
			</p>
		{/if}

	{:else}

		<div class="admin-header">

			<div>
				<h2>Admin Panel</h2>

				<p class="admin-subtitle">
					View recent questions and reported responses.
				</p>
			</div>

			<button
				class="refresh-button"
				onclick={loadData}
				disabled={loading}
			>
				{loading ? 'Refreshing...' : 'Refresh'}
			</button>

		</div>

		{#if error}
			<p class="admin-error">
				{error}
			</p>
		{/if}

		<!-- Reports -->

		<section class="admin-section">

			<div class="section-header">

				<h2>Reports</h2>

				<span class="count">
					{reports.length}
				</span>

			</div>

			{#if loading}

				<p class="admin-muted">
					Loading reports...
				</p>

			{:else if reports.length === 0}

				<p class="admin-muted">
					No reports yet.
				</p>

			{:else}

				{#each reports as row}

					<details class="admin-item">

						<summary>

							<div class="item-summary">

								<strong>
									{formatDate(row[0])}
								</strong>

								<span>
									{row[4]}
								</span>

							</div>

						</summary>

						<div class="item-content">

							<div class="admin-field">

								<strong>Question</strong>

								<p>
									{row[1]}
								</p>

							</div>

							<div class="admin-field">

								<strong>Answer</strong>

								<p>
									{row[2]}
								</p>

							</div>

							<div class="admin-field">

								<strong>Retrieved Regulations</strong>

								{#if parseSources(row[3]).length}

									<ul>
										{#each parseSources(row[3]) as source}

											<li>
												<a
													href={`https://www.worldcubeassociation.org/regulations/#${source.id}`}
													target="_blank"
													rel="noopener noreferrer"
												>
													{source.id}
												</a>
											</li>

										{/each}
									</ul>

								{:else}

									<p class="admin-muted">
										No sources recorded.
									</p>

								{/if}

							</div>

							<div class="admin-field report-comment">

								<strong>Report</strong>

								<p>
									{row[4]}
								</p>

							</div>

						</div>

					</details>

				{/each}

			{/if}

		</section>


		<!-- Questions -->

		<section class="admin-section">

			<div class="section-header">

				<h2>Recent Questions</h2>

				<span class="count">
					{questions.length}
				</span>

			</div>

			{#if loading}

				<p class="admin-muted">
					Loading questions...
				</p>

			{:else if questions.length === 0}

				<p class="admin-muted">
					No questions yet.
				</p>

			{:else}

				{#each questions as row}

					<details class="admin-item">

						<summary>

							{formatDate(row[0])}

						</summary>

						<div class="item-content">

							<div class="admin-field">

								<strong>IP Address</strong>

								<p>
									{row[1]}
								</p>

							</div>

							<div class="admin-field">

								<strong>Question</strong>

								<p>
									{row[2]}
								</p>

							</div>

							<div class="admin-field">

								<strong>Answer</strong>

								<p>
									{row[3]}
								</p>

							</div>

						</div>

					</details>

				{/each}

			{/if}

		</section>

	{/if}

</div>