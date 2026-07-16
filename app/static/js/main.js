// app/static/js/main.js
const botao = document.getElementById('btn-recomendar');
const entrada = document.getElementById('entrada');
const resultado = document.getElementById('resultado');
const sessionId = document.getElementById('session_id').value;

botao.addEventListener('click', async () => {
    const mensagem = entrada.value.trim();
    if (!mensagem) {
        // Exibe um aviso sutil usando a classe de erro (mas sem ícone de erro)
        resultado.innerHTML = `<div class="mensagem-aviso">✍️ Digite algo para receber recomendações!</div>`;
        return;
    }

    resultado.innerHTML = '<div class="mensagem-carregando">⏳ Pensando em boas indicações...</div>';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: mensagem,
                session_id: sessionId
            })
        });

        const dados = await response.json();

        // Se a resposta contém um erro (campo "error"), exibe a mensagem amigável
        if (dados.error) {
            // Usa a classe CSS .mensagem-erro
            resultado.innerHTML = `<div class="mensagem-erro">⚠️ ${dados.error}</div>`;
            return;
        }

        if (dados.response) {
            // Converte quebras de linha para <br> (simples, mas funcional)
            resultado.innerHTML = dados.response.replace(/\n/g, '<br>');
        } else {
            resultado.innerHTML = '<div class="mensagem-aviso">⚠️ Resposta vazia. Tente novamente.</div>';
        }
    } catch (erro) {
        // Erro de rede ou outro problema na comunicação
        resultado.innerHTML = `
            <div class="mensagem-erro">
                ❌ Erro de conexão. Verifique sua internet e tente novamente.
            </div>
        `;
        console.error('Erro na requisição:', erro);
    }
});