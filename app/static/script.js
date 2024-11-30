document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("competencias-form");

    // Adicionar evento de clique para seleção dos botões
    form.addEventListener("click", function (event) {
        if (event.target.classList.contains("option")) {
            const question = event.target.parentElement.dataset.question;

            // Remove a seleção anterior
            document.querySelectorAll(`[data-question="${question}"] .option`).forEach(btn => {
                btn.classList.remove("selected");
            });

            // Adiciona a seleção atual
            event.target.classList.add("selected");
        }
    });

    // Envio dos dados
    document.getElementById("submit-btn").addEventListener("click", function () {
        const selectedValues = {};

        // Coleta os valores selecionados
        document.querySelectorAll(".options").forEach(optionGroup => {
            const question = optionGroup.dataset.question;
            const selectedOption = optionGroup.querySelector(".option.selected");

            if (selectedOption) {
                selectedValues[question] = selectedOption.dataset.value;
            }
        });

        // Verifica se todas as perguntas foram respondidas
        const totalQuestions = document.querySelectorAll(".options").length;
        if (Object.keys(selectedValues).length < totalQuestions) {
            alert("Por favor, responda a todas as perguntas antes de enviar.");
            return;
        }

        // Envio via fetch
        fetch("/submit", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(selectedValues),
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error || "Erro desconhecido"); });
                }
                return response.json();
            })
            .then(data => {
                alert(`Resultado: ${data.resultado}`);
            })
            .catch(error => {
                console.error("Erro:", error.message);
                alert("Erro ao enviar os dados: " + error.message);
            });
    });
});

