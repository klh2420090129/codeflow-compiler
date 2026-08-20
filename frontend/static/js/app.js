const DEFAULT_PROGRAMS = {
    basic: `let x = 10;\nlet y = 20;\nlet z = x + y * 2;\nprint(z);`,
    arithmetic: `let a = 15.5;\nlet b = 4.5;\nlet result = (a + b) * 10 / 2;\nprint(result);`,
    conditions: `let age = 18;\nif (age >= 18) {\n    print(1);\n} else {\n    print(0);\n}`,
    loops: `let count = 0;\nwhile (count < 5) {\n    print(count);\n    count = count + 1;\n}`,
    error_syntax: `let x = ;\nprint(x);`,
    error_semantic: `let a = 10;\nlet b = c + 5;\nprint(b);`
};

let state = {
    result: null,
    selectedPhase: null,
    compiling: false
};

// UI Elements
const els = {
    editor: document.getElementById('source-editor'),
    lineNumbers: document.getElementById('line-numbers'),
    statusIndicator: document.getElementById('status-indicator'),
    statusText: document.getElementById('status-text'),
    exampleSelect: document.getElementById('example-select'),
    traceCheckbox: document.getElementById('trace-checkbox'),
    btnCompileRun: document.getElementById('btn-compile-run'),
    btnCompileOnly: document.getElementById('btn-compile-only'),
    btnClear: document.getElementById('btn-clear'),
    output: document.getElementById('execution-output'),
    inspectorTitle: document.getElementById('inspector-title'),
    inspectorContent: document.getElementById('inspector-content'),
    stages: document.querySelectorAll('.stage')
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    setupEditor();
    setupListeners();
    els.editor.value = DEFAULT_PROGRAMS.basic;
    updateLineNumbers();
});

function setupEditor() {
    els.editor.addEventListener('input', updateLineNumbers);
    els.editor.addEventListener('scroll', () => {
        els.lineNumbers.scrollTop = els.editor.scrollTop;
    });
    els.editor.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = els.editor.selectionStart;
            const end = els.editor.selectionEnd;
            els.editor.value = els.editor.value.substring(0, start) + "    " + els.editor.value.substring(end);
            els.editor.selectionStart = els.editor.selectionEnd = start + 4;
        }
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            compileSource(true);
        }
    });
}

function updateLineNumbers() {
    const lines = els.editor.value.split('\n').length;
    els.lineNumbers.innerHTML = Array.from({length: lines}, (_, i) => i + 1).join('<br>');
}

function setupListeners() {
    els.exampleSelect.addEventListener('change', (e) => {
        if (e.target.value && DEFAULT_PROGRAMS[e.target.value]) {
            els.editor.value = DEFAULT_PROGRAMS[e.target.value];
            updateLineNumbers();
        }
    });

    els.btnCompileRun.addEventListener('click', () => compileSource(true));
    els.btnCompileOnly.addEventListener('click', () => compileSource(false));
    els.btnClear.addEventListener('click', clearAll);

    els.stages.forEach(stage => {
        stage.addEventListener('click', () => {
            selectPhase(stage.dataset.phase);
        });
    });
}

function setStatus(status, text) {
    els.statusIndicator.className = 'status-indicator status-' + status;
    els.statusText.textContent = text;
}

function clearAll() {
    els.editor.value = '';
    updateLineNumbers();
    state.result = null;
    els.output.innerHTML = '<div class="muted">Program not executed.</div>';
    els.inspectorTitle.textContent = 'PHASE INSPECTOR';
    els.inspectorContent.innerHTML = '<div class="muted center-message">Select a pipeline stage to inspect its output.</div>';
    els.stages.forEach(s => {
        s.className = 'stage';
    });
    setStatus('ready', 'READY');
}

async function checkHealth() {
    try {
        const res = await fetch('/api/health');
        if (res.ok) setStatus('ready', 'READY');
        else setStatus('error', 'BACKEND ERROR');
    } catch (e) {
        setStatus('error', 'OFFLINE');
    }
}

async function compileSource(execute) {
    const source = els.editor.value;
    if (!source.trim()) return;

    state.compiling = true;
    setStatus('compiling', 'COMPILING');
    
    // Reset UI
    els.stages.forEach(s => s.className = 'stage');
    els.output.innerHTML = '';
    els.inspectorContent.innerHTML = '<div class="muted center-message">Select a pipeline stage to inspect its output.</div>';

    const trace = els.traceCheckbox.checked;

    try {
        const res = await fetch('/api/compile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source, execute, trace })
        });
        
        state.result = await res.json();
        
        updatePipelineVisuals();
        
        if (state.result.success) {
            setStatus('success', 'SUCCESS');
            renderOutput();
            // Auto select a phase
            selectPhase(execute ? 'vm' : 'target_code');
        } else {
            setStatus('error', 'ERROR');
            renderError();
            // Auto select the phase that failed if known
            if (state.result.error && state.result.error.phase) {
                let phase = state.result.error.phase;
                if (phase === 'optimization') phase = 'optimized_tac';
                if (phase === 'codegen') phase = 'target_code';
                selectPhase(phase);
            }
        }
        
    } catch (e) {
        setStatus('error', 'NETWORK ERROR');
        els.output.innerHTML = `<div style="color:var(--error)">Failed to connect to compiler backend.</div>`;
    } finally {
        state.compiling = false;
    }
}

function updatePipelineVisuals() {
    const r = state.result;
    
    const stageStatus = {
        tokens: r.tokens ? 'success' : 'skipped',
        ast: r.ast ? 'success' : 'skipped',
        symbol_table: r.symbol_table ? 'success' : 'skipped',
        tac: r.tac ? 'success' : 'skipped',
        optimized_tac: r.optimized_tac ? 'success' : 'skipped',
        target_code: r.target_code ? 'success' : 'skipped',
        vm: r.execution_output || r.execution_trace ? 'success' : 'skipped'
    };
    
    if (r.error) {
        let errPhase = r.error.phase;
        if (errPhase === 'lexical') stageStatus.tokens = 'error';
        if (errPhase === 'syntax') stageStatus.ast = 'error';
        if (errPhase === 'semantic') stageStatus.symbol_table = 'error';
        if (errPhase === 'tac') stageStatus.tac = 'error';
        if (errPhase === 'optimization') stageStatus.optimized_tac = 'error';
        if (errPhase === 'codegen') stageStatus.target_code = 'error';
        if (errPhase === 'vm') stageStatus.vm = 'error';
    }
    
    els.stages.forEach(stage => {
        const phase = stage.dataset.phase;
        stage.className = `stage state-${stageStatus[phase]}`;
    });
}

function selectPhase(phase) {
    state.selectedPhase = phase;
    
    els.stages.forEach(s => {
        if (s.dataset.phase === phase) s.classList.add('active');
        else s.classList.remove('active');
    });

    els.inspectorTitle.textContent = phase.toUpperCase().replace('_', ' ') + ' INSPECTOR';
    
    if (!state.result) return;
    
    // Check if there is an error in this phase
    if (state.result.error) {
        let errPhase = state.result.error.phase;
        if (errPhase === 'optimization') errPhase = 'optimized_tac';
        if (errPhase === 'codegen') errPhase = 'target_code';
        if (errPhase === 'lexical') errPhase = 'tokens';
        if (errPhase === 'syntax') errPhase = 'ast';
        if (errPhase === 'semantic') errPhase = 'symbol_table';
        
        if (errPhase === phase) {
            renderPhaseError(state.result.error);
            return;
        }
    }

    if (phase === 'tokens' && state.result.tokens) renderTokens(state.result.tokens);
    else if (phase === 'ast' && state.result.ast) renderAST(state.result.ast);
    else if (phase === 'symbol_table' && state.result.symbol_table) renderSymbolTable(state.result.symbol_table);
    else if (phase === 'tac' && state.result.tac) renderTAC(state.result.tac);
    else if (phase === 'optimized_tac' && state.result.optimized_tac) renderOptimizedTAC(state.result.tac, state.result.optimized_tac);
    else if (phase === 'target_code' && state.result.target_code) renderTargetCode(state.result.target_code);
    else if (phase === 'vm' && state.result.execution_trace) renderTrace(state.result.execution_trace);
    else if (phase === 'vm' && state.result.execution_output) els.inspectorContent.innerHTML = '<div class="muted">Execution completed. Trace not enabled.</div>';
    else els.inspectorContent.innerHTML = '<div class="muted center-message">No data available for this phase.</div>';
}

function renderOutput() {
    if (state.result.execution_output) {
        els.output.innerHTML = state.result.execution_output.map(l => `<div>${l}</div>`).join('') || '<div class="muted">No output produced.</div>';
    } else {
        els.output.innerHTML = '<div class="muted">Program not executed.</div>';
    }
}

function renderError() {
    els.output.innerHTML = `<div style="color:var(--error)">Compilation Failed. See inspector for details.</div>`;
}

function renderPhaseError(error) {
    els.inspectorContent.innerHTML = `
        <div class="error-box">
            <div class="error-title">${error.type || 'Error'}</div>
            <div class="error-msg">${error.message}</div>
            ${error.line ? `<div class="error-loc">Line ${error.line}, Column ${error.column}</div>` : ''}
        </div>
    `;
}

function renderTokens(tokens) {
    let html = `<table class="data-table">
        <tr><th>TYPE</th><th>VALUE</th><th>LINE</th><th>COL</th></tr>`;
    tokens.forEach(t => {
        let val = t.value === '\\n' ? '\\n' : t.value.replace(/</g, '&lt;');
        html += `<tr><td>${t.type}</td><td style="color:var(--accent)">${val}</td><td>${t.line}</td><td>${t.column}</td></tr>`;
    });
    html += `</table>`;
    els.inspectorContent.innerHTML = html;
}

function renderAST(ast) {
    function buildNode(node) {
        if (!node) return '';
        let html = `<div class="ast-node">`;
        let type = node.type || "Node";
        html += `<span class="ast-type">${type}</span>`;
        
        // Primitive fields
        let props = [];
        for (let key in node) {
            if (key !== 'type' && key !== 'line' && key !== 'column') {
                if (typeof node[key] !== 'object' && node[key] !== null) {
                    props.push(`${key}: <span style="color:var(--text-muted)">${node[key]}</span>`);
                }
            }
        }
        if (props.length > 0) html += ` ( ${props.join(', ')} )`;
        
        // Children fields
        let childrenHtml = '';
        for (let key in node) {
            if (key !== 'type' && key !== 'line' && key !== 'column') {
                if (Array.isArray(node[key])) {
                    node[key].forEach(child => {
                        if (typeof child === 'object' && child !== null) {
                            childrenHtml += buildNode(child);
                        }
                    });
                } else if (typeof node[key] === 'object' && node[key] !== null) {
                    childrenHtml += buildNode(node[key]);
                }
            }
        }
        
        if (childrenHtml) {
            html += `<div class="ast-tree">${childrenHtml}</div>`;
        }
        
        html += `</div>`;
        return html;
    }
    
    els.inspectorContent.innerHTML = buildNode(ast);
}

function renderSymbolTable(st) {
    if (!st.scopes) return;
    
    let html = '';
    st.scopes.forEach(scope => {
        html += `<div style="margin-bottom: 20px;">`;
        html += `<div style="color:var(--accent); font-weight:bold; margin-bottom:8px;">SCOPE: ${scope.name}</div>`;
        
        html += `<table class="data-table"><tr><th>NAME</th><th>TYPE</th><th>INITIALIZED</th></tr>`;
        const syms = Object.keys(scope.symbols);
        if (syms.length === 0) {
            html += `<tr><td colspan="3" class="muted">(empty)</td></tr>`;
        } else {
            syms.forEach(s => {
                let sym = scope.symbols[s];
                let init = sym.initialized ? '<span style="color:var(--success)">✓</span>' : '<span style="color:var(--error)">✗</span>';
                html += `<tr><td>${s}</td><td>${sym.type_name}</td><td>${init}</td></tr>`;
            });
        }
        html += `</table></div>`;
    });
    els.inspectorContent.innerHTML = html;
}

function formatTACInstr(t) {
    if (t.type === 'Assignment') return `${t.result} = ${t.arg1}`;
    if (t.type === 'Binary') return `${t.result} = ${t.arg1} ${t.operator} ${t.arg2}`;
    if (t.type === 'Unary') return `${t.result} = ${t.operator}${t.arg1}`;
    if (t.type === 'Label') return `<span style="color:var(--accent)">${t.name}:</span>`;
    if (t.type === 'Goto') return `<span style="color:var(--warning)">GOTO ${t.target}</span>`;
    if (t.type === 'ConditionalJump') return `<span style="color:var(--warning)">IF ${t.jump_if_false ? 'FALSE' : 'TRUE'} ${t.condition} GOTO ${t.target}</span>`;
    if (t.type === 'Print') return `<span style="color:var(--success)">PRINT</span> ${t.value}`;
    return JSON.stringify(t);
}

function renderTAC(tacList) {
    let html = '';
    tacList.forEach((t, i) => {
        let num = String(i).padStart(2, '0');
        let code = formatTACInstr(t);
        html += `<div class="code-block"><div class="code-line-num">${num}</div><div class="code-content">${code}</div></div>`;
    });
    els.inspectorContent.innerHTML = html;
}

function renderOptimizedTAC(original, optimized) {
    let origHtml = '';
    original.forEach((t, i) => {
        origHtml += `<div class="code-block"><div class="code-line-num">${String(i).padStart(2, '0')}</div><div class="code-content">${formatTACInstr(t)}</div></div>`;
    });
    
    let optHtml = '';
    optimized.forEach((t, i) => {
        optHtml += `<div class="code-block"><div class="code-line-num">${String(i).padStart(2, '0')}</div><div class="code-content">${formatTACInstr(t)}</div></div>`;
    });
    
    els.inspectorContent.innerHTML = `
        <div class="opt-compare">
            <div class="opt-pane">
                <div class="opt-title">BEFORE (${original.length} instructions)</div>
                ${origHtml}
            </div>
            <div class="opt-pane">
                <div class="opt-title">AFTER (${optimized.length} instructions)</div>
                ${optHtml}
            </div>
        </div>
    `;
}

function renderTargetCode(code) {
    let html = '';
    code.forEach((t, i) => {
        let num = String(i).padStart(2, '0');
        let opnd = t.operand !== undefined && t.operand !== null ? t.operand : '';
        html += `<div class="code-block"><div class="code-line-num">${num}</div><div class="code-content"><span style="color:var(--accent)">${t.opcode}</span> ${opnd}</div></div>`;
    });
    els.inspectorContent.innerHTML = html;
}

function renderTrace(trace) {
    let html = `<table class="data-table">
        <tr><th>IP</th><th>INSTRUCTION</th><th>STACK</th><th>MEMORY</th></tr>`;
    trace.forEach(t => {
        let stk = JSON.stringify(t.stack);
        let mem = JSON.stringify(t.memory);
        html += `<tr>
            <td style="color:var(--text-muted)">${t.ip}</td>
            <td style="color:var(--accent)">${t.instruction}</td>
            <td>${stk}</td>
            <td><span style="color:var(--text-muted)">${mem}</span></td>
        </tr>`;
    });
    html += `</table>`;
    els.inspectorContent.innerHTML = html;
}
