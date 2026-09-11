const DEFAULT_PROGRAMS = {
    minilang: {
        basic: `let x = 10;\nlet y = 20;\nlet z = x + y * 2;\nprint(z);`,
        arithmetic: `let a = 15.5;\nlet b = 4.5;\nlet result = (a + b) * 10 / 2;\nprint(result);`,
        conditions: `let age = 18;\nif (age >= 18) {\n    print(1);\n} else {\n    print(0);\n}`,
        loops: `let count = 0;\nwhile (count < 5) {\n    print(count);\n    count = count + 1;\n}`,
        error_syntax: `let x = ;\nprint(x);`,
        error_semantic: `let a = 10;\nlet b = c + 5;\nprint(b);`
    },
    python: {
        basic: `x = 10\ny = 20\nz = x + y * 2\nprint(z)`,
        arithmetic: `a = 15.5\nb = 4.5\nresult = (a + b) * 10 / 2\nprint(result)`,
        conditions: `age = 18\nif age >= 18:\n    print(1)\nelse:\n    print(0)`,
        loops: `count = 0\nwhile count < 5:\n    print(count)\n    count = count + 1`,
        error_syntax: `x = \nprint(x)`,
        error_semantic: `a = 10\nb = c + 5\nprint(b)`
    },
    c: {
        basic: `int x = 10;\nint y = 20;\nint z = x + y * 2;\nprintf("%d\\n", z);`,
        arithmetic: `float a = 15.5;\nfloat b = 4.5;\nfloat result = (a + b) * 10 / 2;\nprintf("%f\\n", result);`,
        conditions: `int age = 18;\nif (age >= 18) {\n    printf("%d\\n", 1);\n} else {\n    printf("%d\\n", 0);\n}`,
        loops: `int count = 0;\nwhile (count < 5) {\n    printf("%d\\n", count);\n    count = count + 1;\n}`,
        error_syntax: `int x = ;\nprintf("%d\\n", x);`,
        error_semantic: `int a = 10;\nint b = c + 5;\nprintf("%d\\n", b);`
    },
    javascript: {
        basic: `let x = 10;\nlet y = 20;\nlet z = x + y * 2;\nconsole.log(z);`,
        arithmetic: `let a = 15.5;\nlet b = 4.5;\nlet result = (a + b) * 10 / 2;\nconsole.log(result);`,
        conditions: `let age = 18;\nif (age >= 18) {\n    console.log(1);\n} else {\n    console.log(0);\n}`,
        loops: `let count = 0;\nwhile (count < 5) {\n    console.log(count);\n    count = count + 1;\n}`,
        error_syntax: `let x = ;\nconsole.log(x);`,
        error_semantic: `let a = 10;\nlet b = c + 5;\nconsole.log(b);`
    },
    java: {
        basic: `public class Main {\n    public static void main(String[] args) {\n        int x = 10;\n        int y = 20;\n        int z = x + y * 2;\n        System.out.println(z);\n    }\n}`,
        arithmetic: `public class Main {\n    public static void main(String[] args) {\n        double a = 15.5;\n        double b = 4.5;\n        double result = (a + b) * 10 / 2;\n        System.out.println(result);\n    }\n}`,
        conditions: `public class Main {\n    public static void main(String[] args) {\n        int age = 18;\n        if (age >= 18) {\n            System.out.println(1);\n        } else {\n            System.out.println(0);\n        }\n    }\n}`,
        loops: `public class Main {\n    public static void main(String[] args) {\n        int count = 0;\n        while (count < 5) {\n            System.out.println(count);\n            count = count + 1;\n        }\n    }\n}`,
        error_syntax: `public class Main {\n    public static void main(String[] args) {\n        int x = ;\n        System.out.println(x);\n    }\n}`,
        error_semantic: `public class Main {\n    public static void main(String[] args) {\n        int a = 10;\n        int b = c + 5;\n        System.out.println(b);\n    }\n}`
    },
    cpp: {
        basic: `int main() {\n    int x = 10;\n    int y = 20;\n    int z = x + y * 2;\n    std::cout << z << std::endl;\n}`,
        arithmetic: `int main() {\n    double a = 15.5;\n    double b = 4.5;\n    double result = (a + b) * 10 / 2;\n    std::cout << result << std::endl;\n}`,
        conditions: `int main() {\n    int age = 18;\n    if (age >= 18) {\n        std::cout << 1 << std::endl;\n    } else {\n        std::cout << 0 << std::endl;\n    }\n}`,
        loops: `int main() {\n    int count = 0;\n    while (count < 5) {\n        std::cout << count << std::endl;\n        count = count + 1;\n    }\n}`,
        error_syntax: `int main() {\n    int x = ;\n    std::cout << x << std::endl;\n}`,
        error_semantic: `int main() {\n    int a = 10;\n    int b = c + 5;\n    std::cout << b << std::endl;\n}`
    }
};

let state = {
    result: null,
    selectedPhase: null,
    compiling: false,
    language: 'minilang'
};

// UI Elements
const els = {
    languageSelect: document.getElementById('language-select'),
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
    els.editor.value = DEFAULT_PROGRAMS.minilang.basic;
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
    if (els.languageSelect) {
        els.languageSelect.addEventListener('change', (e) => {
            state.language = e.target.value;
            const placeholders = {
                python: 'Write Python code here...',
                c: 'Write C code here...',
                javascript: 'Write JavaScript code here...',
                java: 'Write Java code here...',
                cpp: 'Write C++ code here...',
                minilang: 'Write MiniLang code here...'
            };
            els.editor.placeholder = placeholders[state.language] || 'Write code here...';
            const langProgs = DEFAULT_PROGRAMS[state.language] || DEFAULT_PROGRAMS.minilang;
            const exVal = els.exampleSelect.value || 'basic';
            els.editor.value = langProgs[exVal] || langProgs.basic;
            updateLineNumbers();
            clearAll(false);
        });
    }

    els.exampleSelect.addEventListener('change', (e) => {
        const langProgs = DEFAULT_PROGRAMS[state.language] || DEFAULT_PROGRAMS.minilang;
        if (e.target.value && langProgs[e.target.value]) {
            els.editor.value = langProgs[e.target.value];
            updateLineNumbers();
        }
    });

    els.btnCompileRun.addEventListener('click', () => compileSource(true));
    els.btnCompileOnly.addEventListener('click', () => compileSource(false));
    els.btnClear.addEventListener('click', () => clearAll(true));

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

function clearAll(clearEditor = true) {
    if (clearEditor) {
        els.editor.value = '';
        updateLineNumbers();
    }
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
    const language = state.language;

    try {
        const res = await fetch('/api/compile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source, execute, trace, language })
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
        cfg: r.cfg ? 'success' : 'skipped',
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
        if (errPhase === 'analysis') stageStatus.cfg = 'error';
        if (errPhase === 'optimization') stageStatus.optimized_tac = 'error';
        if (errPhase === 'codegen') stageStatus.target_code = 'error';
        if (errPhase === 'vm') stageStatus.vm = 'error';
    }
    
    els.stages.forEach(stage => {
        const phase = stage.dataset.phase;
        stage.className = `stage state-${stageStatus[phase] || 'skipped'}`;
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
        if (errPhase === 'analysis') errPhase = 'cfg';
        
        if (errPhase === phase) {
            renderPhaseError(state.result.error);
            return;
        }
    }

    if (phase === 'tokens' && state.result.tokens) renderTokens(state.result.tokens);
    else if (phase === 'ast' && state.result.ast) renderAST(state.result.ast);
    else if (phase === 'symbol_table' && state.result.symbol_table) renderSymbolTable(state.result.symbol_table);
    else if (phase === 'tac' && state.result.tac) renderTAC(state.result.tac);
    else if (phase === 'cfg' && state.result.cfg) renderCFG(state.result.cfg);
    else if (phase === 'optimized_tac' && state.result.optimized_tac) renderOptimizedTAC(state.result.tac, state.result.optimized_tac, state.result.optimization_steps, state.result.optimization_summary);
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

function renderOptimizedTAC(original, optimized, steps, summary) {
    let origHtml = '';
    original.forEach((t, i) => {
        origHtml += `<div class="code-block"><div class="code-line-num">${String(i).padStart(2, '0')}</div><div class="code-content">${formatTACInstr(t)}</div></div>`;
    });
    
    let optHtml = '';
    optimized.forEach((t, i) => {
        optHtml += `<div class="code-block"><div class="code-line-num">${String(i).padStart(2, '0')}</div><div class="code-content">${formatTACInstr(t)}</div></div>`;
    });

    let summaryHtml = '';
    if (summary) {
        summaryHtml = `
            <div class="opt-summary-card">
                <div class="opt-summary-item">
                    <span class="opt-summary-label">Total Steps</span>
                    <span class="opt-summary-val">${summary.total_steps}</span>
                </div>
                <div class="opt-summary-item">
                    <span class="opt-summary-label">Before / After</span>
                    <span class="opt-summary-val">${summary.before_instruction_count} ➔ ${summary.after_instruction_count}</span>
                </div>
                <div class="opt-summary-item">
                    <span class="opt-summary-label">Removed</span>
                    <span class="opt-summary-val" style="color:var(--success)">-${summary.instructions_removed}</span>
                </div>
                <div class="opt-summary-item">
                    <span class="opt-summary-label">Reduction</span>
                    <span class="opt-summary-val" style="color:var(--accent)">${summary.reduction_percentage}%</span>
                </div>
            </div>
        `;
    }

    let traceHtml = '';
    if (steps && steps.length > 0) {
        traceHtml += `<div class="opt-trace-section">`;
        traceHtml += `<div class="opt-trace-header">OPTIMIZATION EXPLANATION TRACE</div>`;
        traceHtml += `<div class="opt-trace-list">`;
        steps.forEach(s => {
            let passBadgeClass = 'opt-badge-prop';
            if (s.pass_name === 'Constant Folding') passBadgeClass = 'opt-badge-fold';
            else if (s.pass_name === 'Algebraic Simplification') passBadgeClass = 'opt-badge-alg';
            else if (s.pass_name === 'Dead Code Elimination') passBadgeClass = 'opt-badge-dce';

            traceHtml += `
                <div class="opt-step-card">
                    <div class="opt-step-top">
                        <div class="opt-step-title">
                            <span class="opt-step-num">#${String(s.step_number).padStart(2, '0')}</span>
                            <span class="opt-badge ${passBadgeClass}">${s.pass_name.toUpperCase()}</span>
                            <span class="opt-rule-tag">${s.rule}</span>
                        </div>
                    </div>
                    <div class="opt-step-transform">
                        <span class="opt-before">${s.before.replace(/</g, '&lt;')}</span>
                        <span class="opt-arrow">➔</span>
                        <span class="opt-after">${s.after.replace(/</g, '&lt;')}</span>
                    </div>
                    <div class="opt-step-explanation">${s.explanation}</div>
                </div>
            `;
        });
        traceHtml += `</div></div>`;
    } else {
        traceHtml = `<div class="opt-trace-section"><div class="opt-trace-header">OPTIMIZATION EXPLANATION TRACE</div><div class="muted center-message" style="height:60px;">No optimization opportunities detected for this code.</div></div>`;
    }
    
    els.inspectorContent.innerHTML = `
        <div class="opt-container">
            ${summaryHtml}
            <div class="opt-compare">
                <div class="opt-pane">
                    <div class="opt-title">BEFORE OPTIMIZATION (${original.length} instructions)</div>
                    ${origHtml}
                </div>
                <div class="opt-pane">
                    <div class="opt-title">AFTER OPTIMIZATION (${optimized.length} instructions)</div>
                    ${optHtml}
                </div>
            </div>
            ${traceHtml}
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

function renderCFG(cfg) {
    if (!cfg || !cfg.blocks || cfg.blocks.length === 0) {
        els.inspectorContent.innerHTML = '<div class="muted center-message">No Control Flow Graph data available.</div>';
        return;
    }

    let html = `<div class="cfg-container">`;

    // Header summary
    html += `
        <div class="cfg-header">
            <span><strong>Blocks:</strong> ${cfg.blocks.length}</span>
            <span><strong>Edges:</strong> ${cfg.edges.length}</span>
            <span><strong>Entry:</strong> <span class="cfg-badge cfg-badge-entry">${cfg.entry || 'None'}</span></span>
            <span><strong>Exits:</strong> ${cfg.exits && cfg.exits.length ? cfg.exits.map(e => `<span class="cfg-badge cfg-badge-exit">${e}</span>`).join(' ') : 'None'}</span>
        </div>
        <div class="cfg-graph-layout">
    `;

    cfg.blocks.forEach(block => {
        const isEntry = block.id === cfg.entry;
        const isExit = cfg.exits && cfg.exits.includes(block.id);
        const cardClass = `cfg-node-card ${isEntry ? 'is-entry' : ''} ${isExit ? 'is-exit' : ''}`;

        html += `<div class="cfg-node-card ${isEntry ? 'is-entry' : ''} ${isExit ? 'is-exit' : ''}">`;

        // Node Header
        html += `
            <div class="cfg-node-header">
                <div class="cfg-node-title">
                    <span>${block.id}</span>
                    ${block.label ? `<span style="color:var(--accent)">[${block.label}:]</span>` : ''}
                    ${isEntry ? '<span class="cfg-badge cfg-badge-entry">ENTRY</span>' : ''}
                    ${isExit ? '<span class="cfg-badge cfg-badge-exit">EXIT</span>' : ''}
                </div>
                <div style="font-size:0.75rem; color:var(--text-muted);">
                    TAC lines [${String(block.start_index).padStart(2, '0')}-${String(block.end_index).padStart(2, '0')}]
                </div>
            </div>
        `;

        // Node Body (Instructions)
        html += `<div class="cfg-node-body">`;
        block.instructions.forEach(instr => {
            html += `<div class="cfg-node-instr">${instr.replace(/</g, '&lt;')}</div>`;
        });
        html += `</div>`;

        // Outgoing edges from this block
        const outgoingEdges = cfg.edges.filter(e => e.from === block.id);

        html += `<div class="cfg-node-footer">`;

        // Predecessors
        html += `<div><strong>Pred:</strong> ${block.predecessors.length > 0 ? block.predecessors.join(', ') : 'none'}</div>`;

        // Successors with Edge Tags
        html += `<div><strong>Succ:</strong> `;
        if (outgoingEdges.length === 0) {
            html += `<span class="muted">none (terminal)</span>`;
        } else {
            outgoingEdges.forEach(e => {
                let tagClass = `cfg-edge-tag cfg-edge-${e.type}`;
                let typeLabel = e.type === 'jump' ? 'JUMP' : (e.type === 'true' ? 'TRUE' : (e.type === 'false' ? 'FALSE' : 'FALLTHROUGH'));
                html += `<span class="${tagClass}">➔ ${e.to} (${typeLabel})</span>`;
            });
        }
        html += `</div>`;

        html += `</div></div>`;
    });

    html += `</div></div>`;
    els.inspectorContent.innerHTML = html;
}
