document.addEventListener("DOMContentLoaded", function () {

    // ─── Upload area drag & drop ──────────────────────────────────────
    const uploadArea = document.getElementById("uploadArea");
    if (uploadArea) {
        const fileInputs = uploadArea.querySelectorAll('input[type="file"]');
        const dropZone = uploadArea.querySelector(".upload-area");

        ["dragenter", "dragover", "dragleave", "drop"].forEach(ev => {
            dropZone.addEventListener(ev, e => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        ["dragenter", "dragover"].forEach(ev => {
            dropZone.addEventListener(ev, () => dropZone.classList.add("dragover"));
        });

        ["dragleave", "drop"].forEach(ev => {
            dropZone.addEventListener(ev, () => dropZone.classList.remove("dragover"));
        });

        dropZone.addEventListener("drop", function (e) {
            const files = e.dataTransfer.files;
            for (const f of files) {
                const name = f.name.toLowerCase();
                let inputName = null;
                if (name === "lx02.xlsx") inputName = "lx02";
                else if (name === "ymm141.xlsx") inputName = "ymm141";
                else if (name === "custos.xlsx") inputName = "custos";
                if (inputName) {
                    const input = document.querySelector(`input[name="${inputName}"]`);
                    if (input) {
                        const dt = new DataTransfer();
                        dt.items.add(f);
                        input.files = dt.files;
                        atualizarStatusArquivo(input);
                    }
                }
            }
        });

        fileInputs.forEach(inp => {
            inp.addEventListener("change", function () { atualizarStatusArquivo(this); });
        });

        function atualizarStatusArquivo(input) {
            const item = input.closest(".arquivo-item");
            if (!item) return;
            const status = item.querySelector(".status");
            if (input.files && input.files[0]) {
                status.textContent = input.files[0].name;
                status.className = "status ok";
            } else {
                const nome = input.name.charAt(0).toUpperCase() + input.name.slice(1) + ".xlsx";
                status.textContent = nome;
                status.className = "status";
            }
        }
    }

    // ─── Aplicar filtros ──────────────────────────────────────────────
    const btnAplicar = document.getElementById("btnAplicar");
    if (btnAplicar) {
        btnAplicar.addEventListener("click", function () {
            const form = document.getElementById("filtrosForm");
            const formData = new FormData(form);

            this.disabled = true;
            this.textContent = "CARREGANDO...";

            const tabelaDiv = document.getElementById("tabelaContainer");
            const totaisDiv = document.getElementById("totaisContainer");
            const loadingMsg = '<div class="loading-overlay"><div class="spinner"></div>Processando...</div>';
            if (tabelaDiv) tabelaDiv.innerHTML = loadingMsg;

            fetch("/aplicar", {
                method: "POST",
                body: formData
            })
                .then(r => r.json())
                .then(data => {
                    if (data.ok) {
                        if (tabelaDiv) tabelaDiv.innerHTML = data.tabela;
                        if (totaisDiv) {
                            totaisDiv.textContent = `Lotes: ${data.totais.lotes}  |  Posicoes: ${data.totais.posicoes}  |  Valor Total: ${data.totais.valor}`;
                        }
                        const btnGerar = document.getElementById("btnGerar");
                        if (btnGerar) {
                            btnGerar.disabled = false;
                            btnGerar.classList.remove("btn-disabled");
                        }
                        reiniciarOrdenacao();
                    } else {
                        if (tabelaDiv) tabelaDiv.innerHTML = `<div class="tabela-mensagem">${data.erro || "Erro desconhecido"}</div>`;
                    }
                })
                .catch(err => {
                    if (tabelaDiv) tabelaDiv.innerHTML = `<div class="tabela-mensagem">Erro de conexao: ${err}</div>`;
                })
                .finally(() => {
                    this.disabled = false;
                    this.textContent = "APLICAR";
                });
        });
    }

    // ─── Gerar documento ──────────────────────────────────────────────
    const btnGerar = document.getElementById("btnGerar");
    if (btnGerar) {
        btnGerar.addEventListener("click", function () {
            const form = document.getElementById("filtrosForm");
            const formData = new FormData(form);

            this.disabled = true;
            this.textContent = "GERANDO...";

            fetch("/gerar", {
                method: "POST",
                body: formData
            })
                .then(r => r.json())
                .then(data => {
                    if (data.ok && data.redirect) {
                        window.location.href = data.redirect;
                    } else {
                        alert("Erro: " + (data.erro || "Erro desconhecido"));
                        this.disabled = false;
                        this.textContent = "GERAR DOCUMENTO";
                    }
                })
                .catch(err => {
                    alert("Erro de conexao: " + err);
                    this.disabled = false;
                    this.textContent = "GERAR DOCUMENTO";
                });
        });
    }

    // ─── Ordenacao da tabela (client-side) ────────────────────────────
    function reiniciarOrdenacao() {
        document.querySelectorAll(".tabela-scroll table th").forEach(th => {
            th.addEventListener("click", function () {
                const table = this.closest("table");
                const chave = this.dataset.chave;
                const tbody = table.querySelector("tbody");
                const rows = Array.from(tbody.querySelectorAll("tr"));
                const colIndex = Array.from(this.parentElement.children).indexOf(this);
                const isAsc = this.dataset.ordem !== "asc";

                document.querySelectorAll("table th .icone-ordem").forEach(i => i.textContent = "");
                this.dataset.ordem = isAsc ? "asc" : "desc";
                this.querySelector(".icone-ordem").textContent = isAsc ? " ▲" : " ▼";

                rows.sort((a, b) => {
                    const aVal = a.children[colIndex]?.textContent.trim() || "";
                    const bVal = b.children[colIndex]?.textContent.trim() || "";
                    const aNum = parseFloat(aVal.replace(/[^0-9,\-]/g, "").replace(",", "."));
                    const bNum = parseFloat(bVal.replace(/[^0-9,\-]/g, "").replace(",", "."));
                    if (!isNaN(aNum) && !isNaN(bNum)) {
                        return isAsc ? aNum - bNum : bNum - aNum;
                    }
                    return isAsc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
                });

                rows.forEach(r => tbody.appendChild(r));
            });
        });
    }
    reiniciarOrdenacao();

    // ─── Historico: busca ─────────────────────────────────────────────
    const historicoBusca = document.getElementById("historicoBusca");
    if (historicoBusca) {
        historicoBusca.addEventListener("keyup", function () {
            const termo = this.value.toLowerCase();
            document.querySelectorAll(".historico-card").forEach(card => {
                const text = card.textContent.toLowerCase();
                card.style.display = text.includes(termo) ? "" : "none";
            });
            const total = document.querySelectorAll('.historico-card[style*="display: none"]').length;
            const visiveis = document.querySelectorAll(".historico-card").length - total;
            const label = document.getElementById("historicoTotal");
            if (label) label.textContent = `${visiveis} de ${document.querySelectorAll(".historico-card").length} geracao(oes)`;
        });
    }

    // ─── Resultado: informar documento ─────────────────────────────────
    document.addEventListener("click", function (e) {
        const btn = e.target.closest("#btnInformarDocumento");
        if (btn) {
            const id = btn.dataset.id;
            const numero = prompt("Digite o numero do documento SAP:");
            if (numero && numero.trim()) {
                const formData = new FormData();
                formData.append("numero", numero.trim());
                fetch(`/atualizar-documento/${id}`, { method: "POST", body: formData })
                    .then(r => r.json())
                    .then(data => {
                        if (data.ok) {
                            alert("Documento salvo com sucesso!");
                        } else {
                            alert("Erro: " + (data.mensagem || data.erro));
                        }
                    })
                    .catch(err => alert("Erro: " + err));
            }
        }
    });

    // ─── Historico: ver resumo ─────────────────────────────────────────
    document.addEventListener("click", function (e) {
        const btn = e.target.closest("[data-acao='ver']");
        if (btn) {
            const id = btn.dataset.id;
            window.location.href = `/resumo-execucao/${id}`;
        }
    });

    // ─── Exclusao de descricao: abrir modal ────────────────────────────
    const btnExcluir = document.getElementById("btnExcluirDescricao");
    const modalExclusao = document.getElementById("modalExclusao");
    if (btnExcluir && modalExclusao) {
        btnExcluir.addEventListener("click", function () {
            fetch("/descricoes")
                .then(r => r.json())
                .then(data => {
                    if (data.erro && !data.descricoes.length) {
                        alert(data.erro);
                        return;
                    }
                    const lista = document.getElementById("modalListaDescricoes");
                    lista.innerHTML = "";
                    const excluidos = new Set(data.excluidos || []);
                    const todos = data.descricoes || [];

                    todos.forEach(desc => {
                        const label = document.createElement("label");
                        label.className = "modal-checkbox-item";
                        const checkbox = document.createElement("input");
                        checkbox.type = "checkbox";
                        checkbox.value = desc;
                        checkbox.checked = !excluidos.has(desc);
                        label.appendChild(checkbox);
                        label.appendChild(document.createTextNode(" " + desc));
                        lista.appendChild(label);
                    });

                    modalExclusao.classList.remove("hidden");

                    const buscaInput = document.getElementById("modalBuscaDescricao");
                    if (buscaInput) {
                        buscaInput.value = "";
                        buscaInput.addEventListener("keyup", function () {
                            const termo = this.value.toLowerCase();
                            document.querySelectorAll("#modalListaDescricoes .modal-checkbox-item").forEach(item => {
                                const texto = item.textContent.toLowerCase();
                                item.style.display = texto.includes(termo) ? "" : "none";
                            });
                        });
                    }
                })
                .catch(err => alert("Erro ao carregar descricoes: " + err));
        });

        document.getElementById("modalExclusaoClose").addEventListener("click", function () {
            modalExclusao.classList.add("hidden");
        });

        document.getElementById("modalCancelarExclusao").addEventListener("click", function () {
            modalExclusao.classList.add("hidden");
        });

        document.getElementById("modalSelecionarTodos").addEventListener("click", function () {
            document.querySelectorAll("#modalListaDescricoes input[type='checkbox']").forEach(cb => cb.checked = true);
        });

        document.getElementById("modalLimparTodos").addEventListener("click", function () {
            document.querySelectorAll("#modalListaDescricoes input[type='checkbox']").forEach(cb => cb.checked = false);
        });

        document.getElementById("modalAplicarExclusao").addEventListener("click", function () {
            const selecionados = [];
            document.querySelectorAll("#modalListaDescricoes input[type='checkbox']:checked").forEach(cb => {
                selecionados.push(cb.value);
            });

            const formData = new FormData();
            selecionados.forEach(s => formData.append("descricoes", s));

            fetch("/aplicar-exclusao", { method: "POST", body: formData })
                .then(r => r.json())
                .then(data => {
                    if (data.ok) {
                        const tabelaDiv = document.getElementById("tabelaContainer");
                        if (tabelaDiv) tabelaDiv.innerHTML = data.tabela;
                        const totaisDiv = document.getElementById("totaisContainer");
                        if (totaisDiv) {
                            totaisDiv.textContent = `Lotes: ${data.totais.lotes}  |  Posicoes: ${data.totais.posicoes}  |  Valor Total: ${data.totais.valor}`;
                        }
                        atualizarStatusExclusao(data.qtd_excluidos);
                        reiniciarOrdenacao();
                        modalExclusao.classList.add("hidden");
                    } else {
                        alert("Erro: " + (data.erro || "Erro desconhecido"));
                    }
                })
                .catch(err => alert("Erro: " + err));
        });

        modalExclusao.addEventListener("click", function (e) {
            if (e.target === modalExclusao) {
                modalExclusao.classList.add("hidden");
            }
        });
    }

    // ─── Exclusao de descricao: limpar ─────────────────────────────────
    const btnLimparExclusao = document.getElementById("btnLimparExclusao");
    if (btnLimparExclusao) {
        btnLimparExclusao.addEventListener("click", function () {
            fetch("/limpar-exclusao", { method: "POST" })
                .then(r => r.json())
                .then(data => {
                    if (data.ok) {
                        const tabelaDiv = document.getElementById("tabelaContainer");
                        if (tabelaDiv) tabelaDiv.innerHTML = data.tabela;
                        const totaisDiv = document.getElementById("totaisContainer");
                        if (totaisDiv) {
                            totaisDiv.textContent = `Lotes: ${data.totais.lotes}  |  Posicoes: ${data.totais.posicoes}  |  Valor Total: ${data.totais.valor}`;
                        }
                        atualizarStatusExclusao(0);
                        reiniciarOrdenacao();
                    } else {
                        alert("Erro: " + (data.erro || "Erro desconhecido"));
                    }
                })
                .catch(err => alert("Erro: " + err));
        });
    }

    function atualizarStatusExclusao(qtd) {
        const status = document.getElementById("statusExclusao");
        const btnLimpar = document.getElementById("btnLimparExclusao");
        if (status) {
            if (qtd > 0) {
                status.textContent = qtd + " descricao(oes) excluida(s)";
                status.className = "status-exc";
            } else {
                status.textContent = "Nenhuma exclusao ativa";
                status.className = "status-exc vazio";
            }
        }
        if (btnLimpar) {
            btnLimpar.style.display = qtd > 0 ? "" : "none";
        }
    }

    // ─── Historico: expandir/recolher ─────────────────────────────────
    document.addEventListener("click", function (e) {
        const btn = e.target.closest("[data-toggle]");
        if (btn && btn.dataset.toggle === "expand") {
            const id = btn.dataset.target;
            const body = document.getElementById(id);
            if (body) {
                const isHidden = body.classList.contains("hidden");
                body.classList.toggle("hidden");
                btn.textContent = body.classList.contains("hidden") ? "Expandir ▼" : "Recolher ▲";

                if (!isHidden) {
                    return;
                }

                const idGeracao = body.dataset.id;
                const loadingDiv = body.querySelector(".detalhes-loading");
                if (loadingDiv) {
                    loadingDiv.textContent = "Carregando detalhes...";
                }

                fetch(`/detalhes-geracao/${idGeracao}`)
                    .then(r => r.json())
                    .then(data => {
                        if (data.ok && data.dados && data.dados.length > 0) {
                            let html = '<div class="tabela-scroll" style="margin-top: 10px;"><table><thead><tr>';
                            data.colunas.forEach(c => {
                                html += `<th>${c.rotulo}</th>`;
                            });
                            html += '</tr></thead><tbody>';
                            data.dados.forEach(row => {
                                html += '<tr>';
                                data.colunas.forEach(c => {
                                    let v = row[c.chave] || "---";
                                    let align = c.chave === "valor_lote" ? ' style="text-align:right"' : '';
                                    html += `<td${align}>${v}</td>`;
                                });
                                html += '</tr>';
                            });
                            html += '</tbody></table></div>';
                            if (loadingDiv) {
                                loadingDiv.outerHTML = html;
                            } else {
                                body.innerHTML = html;
                            }
                        } else {
                            if (loadingDiv) {
                                loadingDiv.textContent = data.erro || "Nenhum detalhe encontrado.";
                            }
                        }
                    })
                    .catch(err => {
                        if (loadingDiv) {
                            loadingDiv.textContent = "Erro ao carregar: " + err;
                        }
                    });
            }
        }
    });

    // ─── Historico: editar documento ──────────────────────────────────
    document.addEventListener("click", function (e) {
        const btn = e.target.closest("[data-acao='editar-doc']");
        if (btn) {
            const id = btn.dataset.id;
            const numero = prompt("Digite o numero do documento SAP:");
            if (numero && numero.trim()) {
                const formData = new FormData();
                formData.append("numero", numero.trim());
                fetch(`/atualizar-documento/${id}`, { method: "POST", body: formData })
                    .then(r => r.json())
                    .then(data => {
                        if (data.ok) {
                            location.reload();
                        } else {
                            alert("Erro: " + data.mensagem);
                        }
                    })
                    .catch(err => alert("Erro: " + err));
            }
        }
    });

    // ─── Historico: excluir geracao ───────────────────────────────────
    document.addEventListener("click", function (e) {
        const btn = e.target.closest("[data-acao='excluir']");
        if (btn) {
            const id = btn.dataset.id;
            const data = btn.dataset.data;
            if (confirm(`Tem certeza que deseja excluir a geracao do dia ${data}? Esta acao nao pode ser desfeita.`)) {
                fetch(`/excluir-geracao/${id}`, { method: "POST" })
                    .then(r => r.json())
                    .then(data => {
                        if (data.ok) {
                            btn.closest(".historico-card").remove();
                        } else {
                            alert("Erro ao excluir.");
                        }
                    })
                    .catch(err => alert("Erro: " + err));
            }
        }
    });

    // ─── Submit do formulario de upload ───────────────────────────────
    const uploadForm = document.getElementById("uploadForm");
    if (uploadForm) {
        uploadForm.addEventListener("submit", function () {
            const btn = this.querySelector("button[type='submit']");
            if (btn) {
                btn.disabled = true;
                btn.textContent = "PROCESSANDO...";
            }
        });
    }
});
