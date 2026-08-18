<script>
	// -------------------------
	// Props
	// -------------------------

	let {
		password,
		questions,
		reports,
		loading,
		loadData
	} = $props();


	// -------------------------
	// API
	// -------------------------

	const API_URL =
		import.meta.env.VITE_API_URL;


	// -------------------------
	// State
	// -------------------------

	let importing = $state(false);
	let importError = $state('');
	let importSuccess = $state('');


	// -------------------------
	// CSV helpers
	// -------------------------

	function escapeCsv(value) {

		if (
			value === null ||
			value === undefined
		) {

			return '';
		}

		const string =
			String(value);

		if (
			string.includes(',') ||
			string.includes('"') ||
			string.includes('\n') ||
			string.includes('\r')
		) {

			return `"${string.replaceAll('"', '""')}"`;
		}

		return string;
	}


	function downloadCsv(
		filename,
		headers,
		rows
	) {

		const csv = [

			headers
				.map(escapeCsv)
				.join(','),

			...rows.map(
				row =>
					row
						.map(escapeCsv)
						.join(',')
			)

		].join('\r\n');


		const blob =
			new Blob(
				[csv],
				{
					type:
						'text/csv;charset=utf-8;'
				}
			);


		const url =
			URL.createObjectURL(blob);


		const link =
			document.createElement('a');

		link.href = url;
		link.download = filename;


		document.body.appendChild(link);

		link.click();

		link.remove();

		URL.revokeObjectURL(url);
	}


	// -------------------------
	// Export questions
	// -------------------------

	function exportQuestions() {

		if (!questions.length) {

			return;
		}

		downloadCsv(
			'questions.csv',

			[
				'timestamp',
				'ip_address',
				'question',
				'answer'
			],

			questions
		);
	}


	// -------------------------
	// Export reports
	// -------------------------

	function exportReports() {

		if (!reports.length) {

			return;
		}

		downloadCsv(
			'reports.csv',

			[
				'timestamp',
				'question',
				'answer',
				'sources',
				'comment'
			],

			reports
		);
	}


	// -------------------------
	// CSV parser
	// -------------------------

	function parseCsv(text) {

		const rows = [];

		let current = '';
		let row = [];
		let quoted = false;


		for (
			let i = 0;
			i < text.length;
			i++
		) {

			const char = text[i];


			// -------------------------
			// Quoted field
			// -------------------------

			if (char === '"') {

				if (
					quoted &&
					text[i + 1] === '"'
				) {

					current += '"';

					i++;

				} else {

					quoted = !quoted;
				}

				continue;
			}


			// -------------------------
			// Column separator
			// -------------------------

			if (
				char === ',' &&
				!quoted
			) {

				row.push(current);

				current = '';

				continue;
			}


			// -------------------------
			// Row separator
			// -------------------------

			if (
				(char === '\n' || char === '\r') &&
				!quoted
			) {

				if (
					char === '\r' &&
					text[i + 1] === '\n'
				) {

					i++;
				}


				row.push(current);


				if (
					row.some(
						value =>
							value.trim() !== ''
					)
				) {

					rows.push(row);
				}


				row = [];
				current = '';

				continue;
			}


			// -------------------------
			// Normal character
			// -------------------------

			current += char;
		}


		// -------------------------
		// Final row
		// -------------------------

		if (
			current ||
			row.length
		) {

			row.push(current);


			if (
				row.some(
					value =>
						value.trim() !== ''
				)
			) {

				rows.push(row);
			}
		}


		return rows;
	}


	// -------------------------
	// Import logs
	// -------------------------

	async function importLogs(event) {

		const file =
			event.target.files?.[0];


		if (!file) {

			return;
		}


		importError = '';
		importSuccess = '';
		importing = true;


		try {

			// -------------------------
			// Read file
			// -------------------------

			const text =
				await file.text();


			const rows =
				parseCsv(text);


			if (rows.length < 2) {

				throw new Error(
					'The CSV file is empty.'
				);
			}


			// -------------------------
			// Identify CSV type
			// -------------------------

			const headers =
				rows[0].map(
					header =>
						header.trim()
				);


			const expectedQuestions = [
				'timestamp',
				'ip_address',
				'question',
				'answer'
			];


			const expectedReports = [
				'timestamp',
				'question',
				'answer',
				'sources',
				'comment'
			];


			let type;


			if (
				headers.length ===
					expectedQuestions.length &&
				headers.every(
					(header, index) =>
						header ===
						expectedQuestions[index]
				)
			) {

				type = 'questions';

			} else if (
				headers.length ===
					expectedReports.length &&
				headers.every(
					(header, index) =>
						header ===
						expectedReports[index]
				)
			) {

				type = 'reports';

			} else {

				throw new Error(
					'Unrecognised CSV format.'
				);
			}


			// -------------------------
			// Data rows
			// -------------------------

			const dataRows =
				rows.slice(1);


			// -------------------------
			// Upload to API
			// -------------------------

			const response =
				await fetch(
					`${API_URL}/import-logs`,
					{
						method: 'POST',

						headers: {
							'Content-Type':
								'application/json'
						},

						body: JSON.stringify({
							password,
							type,
							rows: dataRows
						})
					}
				);


			const data =
				await response.json();


			if (!response.ok) {

				throw new Error(
					data.detail ||
					'Import failed.'
				);
			}


			// -------------------------
			// Success
			// -------------------------

			importSuccess =
				`Imported ${data.imported} ${type} successfully.`;


			await loadData();

		} catch (err) {

			console.error(err);

			importError =
				err.message ||
				'Failed to import CSV.';

		} finally {

			importing = false;


			// Allow selecting the
			// same file again.

			event.target.value = '';
		}
	}
</script>


<section class="admin-tools">

	<h2>Data</h2>

	<p>
		Export logs for backup or analysis,
		or import a previously exported CSV.
	</p>


	<div class="admin-tools-buttons">

		<!-- Export questions -->

		<button
			type="button"
			onclick={exportQuestions}
			disabled={
				loading ||
				questions.length === 0
			}
		>
			Export Questions
		</button>


		<!-- Export reports -->

		<button
			type="button"
			onclick={exportReports}
			disabled={
				loading ||
				reports.length === 0
			}
		>
			Export Reports
		</button>


		<!-- Import -->

		<label class="import-button">

			{importing
				? 'Importing...'
				: 'Import CSV'}

			<input
				type="file"
				accept=".csv,text/csv"
				onchange={importLogs}
				disabled={importing}
				hidden
			/>

		</label>

	</div>


	<!-- Import error -->

	{#if importError}

		<p class="admin-error">
			{importError}
		</p>

	{/if}


	<!-- Import success -->

	{#if importSuccess}

		<p class="admin-success">
			{importSuccess}
		</p>

	{/if}

</section>