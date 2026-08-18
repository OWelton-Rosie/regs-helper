<script>
	let {
		password = $bindable(''),
		error = '',
		login
	} = $props();
</script>

<h1>Hi Oscar!</h1>

<p>
	Enter the password to view the admin panel.
</p>

<input
	type="password"
	bind:value={password}
	placeholder="Password"
	onkeydown={(e) =>
		e.key === 'Enter' && login()}
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