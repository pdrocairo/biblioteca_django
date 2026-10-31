// ============================================================
// BiblioTech — front mínimo em JS puro, consumindo a API DRF
// ============================================================

// Endereço base da API Django. Definido em config.js; ajuste lá se o
// servidor rodar em outra porta/host.
const API_BASE = window.BIBLIOTECH_API_BASE || "http://127.0.0.1:8000/api";

// Referências dos elementos da tela
const telaLogin = document.getElementById("tela-login");
const telaApp = document.getElementById("tela-app");
const formLogin = document.getElementById("form-login");
const erroLogin = document.getElementById("erro-login");
const listaLivros = document.getElementById("lista-livros");
const aviso = document.getElementById("aviso");
const btnLogout = document.getElementById("btn-logout");
const btnRecarregar = document.getElementById("btn-recarregar");

const modal = document.getElementById("modal-emprestimo");
const modalTitulo = document.getElementById("modal-livro-titulo");
const modalInputUsuario = document.getElementById("modal-id-usuario");
const modalConfirmar = document.getElementById("modal-confirmar");
const modalCancelar = document.getElementById("modal-cancelar");

// Guarda em memória o que o modal precisa saber quando o usuário confirmar
let modalContexto = null; // { modo: "emprestar" | "devolver", livroId, exemplarId }

// --------------------------------------------------------------
// Autenticação (JWT)
// --------------------------------------------------------------

function getToken() {
  return localStorage.getItem("bibliotech_access");
}

function salvarToken(token) {
  localStorage.setItem("bibliotech_access", token);
}

function limparToken() {
  localStorage.removeItem("bibliotech_access");
}

// Wrapper em cima do fetch: já injeta o header Authorization
// (o mesmo header que testávamos manualmente no Postman/Insomnia).
async function apiFetch(caminho, opcoes = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(opcoes.headers || {}),
  };

  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const resposta = await fetch(`${API_BASE}${caminho}`, { ...opcoes, headers });
  return resposta;
}

async function fazerLogin(username, password) {
  const resposta = await fetch(`${API_BASE}/token/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (!resposta.ok) {
    throw new Error("Usuário ou senha inválidos.");
  }

  const dados = await resposta.json();
  salvarToken(dados.access);
}

formLogin.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  erroLogin.hidden = true;

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  try {
    await fazerLogin(username, password);
    mostrarApp();
  } catch (erro) {
    erroLogin.textContent = erro.message;
    erroLogin.hidden = false;
  }
});

btnLogout.addEventListener("click", () => {
  limparToken();
  mostrarLogin();
});

function mostrarApp() {
  telaLogin.hidden = true;
  telaApp.hidden = false;
  carregarAcervo();
}

function mostrarLogin() {
  telaApp.hidden = true;
  telaLogin.hidden = false;
}

// --------------------------------------------------------------
// Carregar livros + exemplares e desenhar os cartões
// --------------------------------------------------------------

async function carregarAcervo() {
  listaLivros.innerHTML = `<p class="carregando">Consultando o acervo…</p>`;

  try {
    const [respLivros, respExemplares] = await Promise.all([
      apiFetch("/livros/"),
      apiFetch("/exemplares/"),
    ]);

    if (respLivros.status === 401 || respExemplares.status === 401) {
      // Token expirou ou é inválido — manda de volta pro login
      limparToken();
      mostrarLogin();
      return;
    }

    const livros = await respLivros.json();
    const exemplares = await respExemplares.json();

    desenharCartoes(livros, exemplares);
  } catch (erro) {
    listaLivros.innerHTML = `<p class="carregando">Não foi possível consultar o acervo. O servidor Django está rodando?</p>`;
  }
}

function desenharCartoes(livros, exemplares) {
  if (livros.length === 0) {
    listaLivros.innerHTML = `<p class="carregando">Nenhum livro cadastrado ainda.</p>`;
    return;
  }

  listaLivros.innerHTML = "";

  livros.forEach((livro) => {
    // Exemplares que pertencem a este livro
    const exemplaresDoLivro = exemplares.filter((ex) => ex.livro === livro.id);
    const exemplarDisponivel = exemplaresDoLivro.find((ex) => ex.disponivel === true);
    const exemplarEmprestado = exemplaresDoLivro.find((ex) => ex.disponivel === false);

    const cartao = document.createElement("article");
    cartao.className = "cartao-livro";

    cartao.innerHTML = `
      <span class="selo ${exemplarDisponivel ? "disponivel" : "indisponivel"}">
        ${exemplarDisponivel ? "Disponível" : "Emprestado"}
      </span>
      <h3 class="cartao-titulo">${livro.titulo}</h3>
      <div class="cartao-meta">
        <span><b>Autor:</b> ${livro.autor_nome ?? "—"}</span>
        <span><b>Categoria:</b> ${livro.categoria_nome ?? "—"}</span>
        <span><b>Editora:</b> ${livro.editora_nome ?? "—"}</span>
      </div>
    `;

    const botao = document.createElement("button");
    if (exemplarDisponivel) {
      botao.textContent = "Registrar retirada";
      botao.className = "btn-emprestar";
      botao.addEventListener("click", () => abrirModal("emprestar", livro));
    } else if (exemplarEmprestado) {
      botao.textContent = "Registrar devolução";
      botao.className = "btn-devolver";
      botao.addEventListener("click", () => abrirModal("devolver", livro, exemplarEmprestado));
    } else {
      botao.textContent = "Sem exemplares";
      botao.disabled = true;
    }

    cartao.appendChild(botao);
    listaLivros.appendChild(cartao);
  });
}

// --------------------------------------------------------------
// Modal de empréstimo / devolução
// --------------------------------------------------------------

function abrirModal(modo, livro, exemplar = null) {
  modalContexto = { modo, livroId: livro.id, exemplarId: exemplar ? exemplar.id : null };
  modalTitulo.textContent = livro.titulo;
  modalConfirmar.textContent = modo === "emprestar" ? "Carimbar retirada" : "Carimbar devolução";
  modalInputUsuario.value = "";
  modal.hidden = false;
  modalInputUsuario.focus();
}

function fecharModal() {
  modal.hidden = true;
  modalContexto = null;
}

modalCancelar.addEventListener("click", fecharModal);

modalConfirmar.addEventListener("click", async () => {
  if (!modalContexto) return;

  const idUsuario = modalInputUsuario.value;
  if (!idUsuario) {
    modalInputUsuario.focus();
    return;
  }

  try {
    if (modalContexto.modo === "emprestar") {
      await registrarEmprestimo(idUsuario, modalContexto.livroId);
      mostrarAviso("Retirada registrada com sucesso.");
    } else {
      await registrarDevolucao(idUsuario, modalContexto.exemplarId);
      mostrarAviso("Devolução registrada com sucesso.");
    }
    fecharModal();
    carregarAcervo();
  } catch (erro) {
    mostrarAviso(erro.message, true);
  }
});

async function registrarEmprestimo(idUsuario, idLivro) {
  const resposta = await apiFetch("/emprestimos/registrar_emprestimo/", {
    method: "POST",
    body: JSON.stringify({ id_usuario: idUsuario, id_livro: idLivro }),
  });

  const dados = await resposta.json();
  if (!resposta.ok) {
    throw new Error(dados.erro || dados.detail || "Não foi possível registrar a retirada.");
  }
}

async function registrarDevolucao(idUsuario, idExemplar) {
  const resposta = await apiFetch("/emprestimos/registrar_devolucoes/", {
    method: "PATCH",
    body: JSON.stringify({ id_usuario: idUsuario, id_exemplar: idExemplar }),
  });

  const dados = await resposta.json();
  if (!resposta.ok) {
    throw new Error(dados.erro || dados.detail || "Não foi possível registrar a devolução.");
  }
}

function mostrarAviso(texto, isErro = false) {
  aviso.textContent = texto;
  aviso.hidden = false;
  aviso.classList.toggle("erro-aviso", isErro);
  setTimeout(() => { aviso.hidden = true; }, 4000);
}

btnRecarregar.addEventListener("click", carregarAcervo);

// --------------------------------------------------------------
// Ponto de entrada: se já existe token salvo, pula o login
// --------------------------------------------------------------

if (getToken()) {
  mostrarApp();
} else {
  mostrarLogin();
}
