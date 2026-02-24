// ── Formatação de campos ──────────────────────────────────────
function fmtCPF(v) {
  const n = v.replace(/\D/g,"").slice(0,11);
  return n.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/,"$1.$2.$3-$4")
           .replace(/(\d{3})(\d{3})(\d{1,3})$/,"$1.$2.$3")
           .replace(/(\d{3})(\d{1,3})$/,"$1.$2");
}
function fmtCNPJ(v) {
  const n = v.replace(/\D/g,"").slice(0,14);
  return n.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/,"$1.$2.$3/$4-$5")
           .replace(/(\d{2})(\d{3})(\d{3})(\d{1,4})$/,"$1.$2.$3/$4")
           .replace(/(\d{2})(\d{3})(\d{1,3})$/,"$1.$2.$3")
           .replace(/(\d{2})(\d{1,3})$/,"$1.$2");
}
function fmtTel(v) {
  const n = v.replace(/\D/g,"").slice(0,11);
  if(n.length<=2) return n.length ? "("+n : "";
  if(n.length<=6) return `(${n.slice(0,2)}) ${n.slice(2)}`;
  if(n.length<=10) return `(${n.slice(0,2)}) ${n.slice(2,6)}-${n.slice(6)}`;
  return `(${n.slice(0,2)}) ${n.slice(2,7)}-${n.slice(7)}`;
}
function fmtCEP(v) {
  const n = v.replace(/\D/g,"").slice(0,8);
  return n.length > 5 ? `${n.slice(0,5)}-${n.slice(5)}` : n;
}
function fmtData(v) {
  const n = v.replace(/\D/g,"").slice(0,8);
  if(n.length<=2) return n;
  if(n.length<=4) return `${n.slice(0,2)}/${n.slice(2)}`;
  return `${n.slice(0,2)}/${n.slice(2,4)}/${n.slice(4)}`;
}

function aplicarFmt(el, fn) {
  el.addEventListener("input", function() {
    const pos = this.selectionStart;
    const old = this.value;
    this.value = fn(this.value);
    // reposicionar cursor aproximadamente
    const diff = this.value.length - old.length;
    this.setSelectionRange(pos + diff, pos + diff);
  });
}

// ── Busca com debounce ────────────────────────────────────────
// url: destino da busca (ex: '/clientes' ou '/produtos')
function initBusca(url) {
  const inp = document.getElementById("busca");
  if (!inp || !url) return;
  // Foco no fim do texto
  const v = inp.value; inp.value = ''; inp.value = v;
  inp.focus();
  let timer;
  inp.addEventListener("input", function() {
    clearTimeout(timer);
    const q = this.value.trim();
    if (q.length < 3) return;
    timer = setTimeout(() => {
      window.location.href = url + '?q=' + encodeURIComponent(q);
    }, 400);
  });
}

// ── Blocos dinâmicos (dependentes / autorizados) ──────────────
function initBlocosDinamicos(containerId, prefix, max, campos) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const INP = "background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:12px;color:#f8fafc;font-family:inherit;font-size:0.875rem;padding:10px 14px;outline:none;width:100%;transition:border-color .2s;";

  function criarBloco(idx) {
    const div = document.createElement("div");
    div.className = "sub-bloco-new";
    div.dataset.idx = idx;
    div.style.cssText = "background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:14px 16px;margin-bottom:10px;";

    let html = `<div style="display:flex;gap:12px;align-items:center;">`;

    campos.forEach(c => {
      if (c.type === "check") {
        html += `<div style="display:flex;align-items:center;padding-top:2px;flex-shrink:0;">
          <input type="checkbox" id="${prefix}${idx}_${c.key}" name="${prefix}${idx}_${c.key}" value="1"
                 style="width:18px;height:18px;accent-color:#38bdf8;cursor:pointer;flex-shrink:0;">
        </div>`;
      } else {
        const flexVal = c.flex !== undefined ? c.flex : 1;
        html += `<div style="flex:${flexVal};min-width:0;">
          <input type="text" name="${prefix}${idx}_${c.key}" placeholder="${c.label}${c.ph ? ' — '+c.ph : ''}"
                 data-fmt="${c.fmt||""}" style="${INP}">
        </div>`;
      }
    });

    html += `<button type="button" onclick="remBloco(this,'${containerId}','${prefix}')"
      style="background:transparent;border:none;color:rgba(248,113,113,0.5);cursor:pointer;font-size:18px;padding:0 4px;flex-shrink:0;line-height:1;transition:color .2s;"
      onmouseover="this.style.color='#f87171'" onmouseout="this.style.color='rgba(248,113,113,0.5)'">✕</button>`;
    html += `</div>`;
    div.innerHTML = html;

    // Focus style + validação CPF inline
    div.querySelectorAll("input[type=text]").forEach(el => {
      el.addEventListener("focus", () => el.style.borderColor = "rgba(56,189,248,0.5)");
      el.addEventListener("blur", () => {
        el.style.borderColor = "rgba(255,255,255,0.08)";
        if (el.dataset.fmt === "cpf" && el.value.trim()) {
          const ok = validarCPF(el.value);
          // remove msg anterior
          const prev = el.parentElement.querySelector(".cpf-msg");
          if (prev) prev.remove();
          const msg = document.createElement("span");
          msg.className = "cpf-msg";
          msg.style.cssText = "font-size:10px;font-weight:700;letter-spacing:.05em;margin-top:3px;display:block;";
          if (ok) {
            msg.textContent = "CPF válido ✓";
            msg.style.color = "#4ade80";
            el.style.borderColor = "rgba(255,255,255,0.08)";
            el.dataset.valido = "1";
          } else {
            msg.textContent = "CPF inválido — verifique.";
            msg.style.color = "#f87171";
            el.style.borderColor = "#f87171";
            el.dataset.valido = "0";
          }
          el.parentElement.appendChild(msg);
        }
      });
    });

    // Aplicar formatação
    div.querySelectorAll("[data-fmt]").forEach(el => {
      const fn = {cpf:fmtCPF, tel:fmtTel}[el.dataset.fmt];
      if (fn) aplicarFmt(el, fn);
    });

    return div;
  }

  // Botão adicionar
  const btn = document.createElement("button");
  btn.type = "button";
  btn.style.cssText = "width:100%;padding:10px;background:transparent;border:1px dashed rgba(56,189,248,0.2);border-radius:12px;color:rgba(56,189,248,0.5);font-family:inherit;font-size:0.78rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;cursor:pointer;margin-top:4px;transition:all .2s;";
  btn.innerHTML = `+ ${prefix === "dep" ? "Dependente" : "Autorizado"}`;
  btn.onmouseover = () => { btn.style.borderColor="rgba(56,189,248,0.5)"; btn.style.color="#38bdf8"; };
  btn.onmouseout  = () => { btn.style.borderColor="rgba(56,189,248,0.2)"; btn.style.color="rgba(56,189,248,0.5)"; };
  btn.onclick = () => {
    const blocos = container.querySelectorAll(".sub-bloco-new");
    const atual = blocos.length;
    if (atual >= max) return;

    // Verificar se o último bloco está completo (CPF e Nome preenchidos)
    if (atual > 0) {
      const ultimo = blocos[blocos.length - 1];
      const cpfEl  = ultimo.querySelector("input[data-fmt='cpf']");
      const nomeEl = ultimo.querySelector("input:not([data-fmt]):not([type='checkbox'])");
      const cpfOk  = cpfEl  && cpfEl.value.replace(/\D/g,'').length === 11 && cpfEl.dataset.valido !== "0";
      const nomeOk = nomeEl && nomeEl.value.trim().length > 1;
      if (!cpfOk || !nomeOk) {
        // Piscar borda do campo incompleto
        [cpfEl, nomeEl].forEach(el => {
          if (!el) return;
          const vazio = el === cpfEl ? !cpfOk : !nomeOk;
          if (vazio) {
            el.style.borderColor = '#f87171';
            el.focus();
            setTimeout(() => el.style.borderColor = 'rgba(255,255,255,0.08)', 2000);
          }
        });
        return;
      }
    }

    const idx = atual + 1;
    container.insertBefore(criarBloco(idx), btn);
    if (atual + 1 >= max) btn.style.display = "none";
  };
  container.appendChild(btn);

  window.remBloco = function(el, cid, pfx) {
    const c = document.getElementById(cid);
    el.closest(".sub-bloco-new").remove();
    // Renumerar
    c.querySelectorAll(".sub-bloco-new").forEach((b, i) => {
      b.dataset.idx = i + 1;
      b.querySelector(".sub-bloco-num").textContent =
        (pfx === "dep" ? "Dependente" : "Autorizado") + " " + (i + 1);
      b.querySelectorAll("[name]").forEach(inp => {
        inp.name = inp.name.replace(/\d+/, i + 1);
        if (inp.id) inp.id = inp.id.replace(/\d+/, i + 1);
        if (inp.htmlFor) inp.htmlFor = inp.htmlFor.replace(/\d+/, i + 1);
      });
    });
    const btn = c.querySelector(".btn-add-sub");
    if (btn) btn.style.display = "";
  };
}

// ── Init ao carregar ─────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  // Formatar campos existentes na página
  document.querySelectorAll("[data-fmt]").forEach(el => {
    const fns = {cpf:fmtCPF, cnpj:fmtCNPJ, tel:fmtTel, cep:fmtCEP, data:fmtData};
    const fn = fns[el.dataset.fmt];
    if (fn) aplicarFmt(el, fn);
  });
});

// ── Corrige fundo branco ao voltar pelo navegador (bfcache) ──
function fixInputStyles() {
  document.querySelectorAll("input, textarea, select").forEach(el => {
    el.style.backgroundColor = "transparent";
    el.style.color = el.readOnly || el.disabled ? "#94a3b8" : "#f8fafc";
  });
}

// Ao voltar pelo bfcache (pageshow), reaplicar estilos
window.addEventListener("pageshow", (e) => {
  if (e.persisted) fixInputStyles();
});

// Também chamar no DOMContentLoaded para cobrir o caso normal
document.addEventListener("DOMContentLoaded", fixInputStyles);

// ── Consulta ViaCEP ───────────────────────────────────────────
function initCEP(cepId, ruaId, bairroId, cidadeId, estadoId) {
  const cepEl = document.getElementById(cepId);
  if (!cepEl || cepEl.readOnly) return;

  cepEl.addEventListener("blur", async function() {
    const digits = this.value.replace(/\D/g, "");
    if (digits.length !== 8) return;

    try {
      const r = await fetch(`https://viacep.com.br/ws/${digits}/json/`);
      const d = await r.json();
      if (d.erro) {
        showCepMsg(cepEl, "CEP não encontrado — preencha manualmente.", "erro");
        return;
      }
      const set = (id, v) => { const el = document.getElementById(id); if (el && v) el.value = v; };
      set(ruaId,    d.logradouro);
      set(bairroId, d.bairro);
      set(cidadeId, d.localidade);
      const sel = document.getElementById(estadoId);
      if (sel && d.uf) sel.value = d.uf;
      showCepMsg(cepEl, "Endereço preenchido ✓", "ok");
    } catch {
      showCepMsg(cepEl, "Erro ao consultar CEP — preencha manualmente.", "erro");
    }
  });
}

function showCepMsg(cepEl, msg, tipo) {
  let span = cepEl.parentElement.querySelector(".cep-msg");
  if (!span) {
    span = document.createElement("span");
    span.className = "cep-msg";
    cepEl.parentElement.appendChild(span);
  }
  span.textContent = msg;
  span.style.cssText = `font-size:10px; font-weight:700; letter-spacing:.05em; margin-top:4px; display:block;
    color: ${tipo === "ok" ? "#4ade80" : "#f87171"};`;
  setTimeout(() => span.remove(), 4000);
}

// ── Validação CPF / CNPJ ──────────────────────────────────────
function validarCPF(v) {
  const n = v.replace(/\D/g,"");
  if (n.length !== 11 || /^(\d)\1+$/.test(n)) return false;
  let s = 0;
  for (let i=0; i<9; i++) s += +n[i] * (10-i);
  let r = (s*10) % 11; if (r===10||r===11) r=0;
  if (r !== +n[9]) return false;
  s = 0;
  for (let i=0; i<10; i++) s += +n[i] * (11-i);
  r = (s*10) % 11; if (r===10||r===11) r=0;
  return r === +n[10];
}

function validarCNPJ(v) {
  const n = v.replace(/\D/g,"");
  if (n.length !== 14 || /^(\d)\1+$/.test(n)) return false;
  const calc = (t) => {
    let s=0, p=t.length-7;
    for (let i=0; i<t.length; i++) { s += +n[i]*p--; if(p<2) p=9; }
    const r = s%11; return r<2 ? 0 : 11-r;
  };
  return calc(n.slice(0,12))===+n[12] && calc(n.slice(0,13))===+n[13];
}

function initValidacaoDoc(inputId, tipo) {
  const el = document.getElementById(inputId);
  if (!el || el.readOnly) return;

  el.addEventListener("blur", function() {
    const raw = this.value.replace(/\D/g,"");
    if (!raw) return;
    const ok = tipo === "cpf" ? validarCPF(raw) : validarCNPJ(raw);
    let msg = el.parentElement.querySelector(".doc-msg");
    if (!msg) {
      msg = document.createElement("span");
      msg.className = "doc-msg";
      el.parentElement.appendChild(msg);
    }
    if (ok) {
      msg.textContent = tipo.toUpperCase() + " válido ✓";
      msg.style.cssText = "font-size:10px;font-weight:700;letter-spacing:.05em;margin-top:4px;display:block;color:#4ade80;";
      el.style.borderColor = "";
      el.dataset.valido = "1";
    } else {
      msg.textContent = tipo.toUpperCase() + " inválido — verifique os dígitos.";
      msg.style.cssText = "font-size:10px;font-weight:700;letter-spacing:.05em;margin-top:4px;display:block;color:#f87171;";
      el.style.borderColor = "#f87171";
      el.dataset.valido = "0";
    }
  });
}

// Bloquear submit se qualquer CPF/CNPJ do form for inválido
function initFormValidacao(formId, docInputId) {
  const form = document.getElementById(formId);
  if (!form) return;
  form.addEventListener("submit", function(e) {
    // Validar campo principal (CPF titular ou CNPJ)
    const principal = document.getElementById(docInputId);
    if (principal) {
      const raw = principal.value.replace(/\D/g,"");
      if (raw) {
        const tipo = principal.dataset.fmt;
        const ok = tipo === "cpf" ? validarCPF(raw) : validarCNPJ(raw);
        if (!ok) {
          e.preventDefault();
          principal.dispatchEvent(new Event("blur"));
          principal.focus();
          return;
        }
      }
    }

    // Validar todos os CPFs de dependentes/autorizados
    const cpfFields = form.querySelectorAll("input[data-fmt='cpf']:not(#" + docInputId + ")");
    for (const el of cpfFields) {
      const raw = el.value.replace(/\D/g,"");
      if (!raw) continue; // campo vazio — ok, é opcional
      if (!validarCPF(raw)) {
        e.preventDefault();
        el.style.borderColor = "#f87171";
        el.focus();
        // Mostrar mensagem
        const prev = el.parentElement.querySelector(".cpf-msg");
        if (prev) prev.remove();
        const msg = document.createElement("span");
        msg.className = "cpf-msg";
        msg.style.cssText = "font-size:10px;font-weight:700;letter-spacing:.05em;margin-top:3px;display:block;color:#f87171;";
        msg.textContent = "CPF inválido — verifique.";
        el.parentElement.appendChild(msg);
        return;
      }
    }
  });
}
