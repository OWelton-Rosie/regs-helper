<script>
	import Header from '$lib/components/Header.svelte';

	import AdminLogin from './components/AdminLogin.svelte';
	import AdminHeader from './components/AdminHeader.svelte';
	import AdminTools from './components/AdminTools.svelte';
	import Reports from './components/Reports.svelte';
	import Questions from './components/Questions.svelte';


	// -------------------------
	// API
	// -------------------------

	const API_URL =
		import.meta.env.VITE_API_URL;


	// -------------------------
	// State
	// -------------------------

	let password = $state('');
	let loggedIn = $state(false);
	let error = $state('');

	let questions = $state([]);
	let reports = $state([]);

	let loading = $state(false);


	// -------------------------
	// Login
	// -------------------------

	async function login() {

		error = '';

		if (!password.trim()) {

			error =
				'Please enter the password';

			return;
		}

		try {

			const response =
				await fetch(
					`${API_URL}/login`,
					{
						method: 'POST',

						headers: {
							'Content-Type':
								'application/json'
						},

						body: JSON.stringify({
							password
						})
					}
				);

			if (!response.ok) {

				error =
					'Incorrect password';

				return;
			}

			loggedIn = true;

			await loadData();

		} catch (err) {

			console.error(err);

			error =
				'Login failed';
		}
	}


	// -------------------------
	// Load data
	// -------------------------

	async function loadData() {

		loading = true;
		error = '';

		try {

			const [
				questionsResponse,
				reportsResponse
			] = await Promise.all([

				fetch(
					`${API_URL}/questions`,
					{
						method: 'POST',

						headers: {
							'Content-Type':
								'application/json'
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
							'Content-Type':
								'application/json'
						},

						body: JSON.stringify({
							password
						})
					}
				)

			]);

			if (!questionsResponse.ok) {

				throw new Error(
					'Failed to load questions'
				);
			}

			if (!reportsResponse.ok) {

				throw new Error(
					'Failed to load reports'
				);
			}

			const questionsData =
				await questionsResponse.json();

			const reportsData =
				await reportsResponse.json();

			questions =
				questionsData.questions;

			reports =
				reportsData.reports;

		} catch (err) {

			console.error(err);

			error =
				'Failed to load admin data';

		} finally {

			loading = false;
		}
	}
</script>


<Header />


<div class="container">

	{#if !loggedIn}

		<AdminLogin
			bind:password
			{error}
			{login}
		/>

	{:else}

		<AdminHeader
			{loading}
			{loadData}
		/>


		{#if error}

			<p class="admin-error">
				{error}
			</p>

		{/if}


		<AdminTools
			{password}
			{questions}
			{reports}
			{loading}
			{loadData}
		/>


		<Reports
			{reports}
			{loading}
		/>


		<Questions
			{questions}
			{loading}
		/>

	{/if}

</div>