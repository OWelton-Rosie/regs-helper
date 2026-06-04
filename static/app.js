async function askQuestion() {

    const question =
        document.getElementById("question").value;

    const answerDiv =
        document.getElementById("answer");

    const sourcesDiv =
        document.getElementById("sources");

    // Show answer box while loading
    answerDiv.style.display = "block";
    answerDiv.innerText =
        "Searching regulations...";

    // Hide sources until we have results
    sourcesDiv.style.display = "none";
    sourcesDiv.innerHTML = "";

    try {

        const response = await fetch(
            `/ask?question=${encodeURIComponent(question)}`
        );

        const data = await response.json();

        answerDiv.innerText =
            data.answer;

        let html =
            "<h2>Retrieved Regulations</h2>";

        data.sources.forEach(source => {

            html += `
                <details>
                    <summary>${source.id}</summary>
                    <p>${source.text}</p>
                </details>
            `;
        });

        sourcesDiv.innerHTML = html;
        sourcesDiv.style.display = "block";

    } catch (error) {

        console.error(error);

        answerDiv.style.display = "block";
        answerDiv.innerText =
            "Something went wrong.";
    }
}