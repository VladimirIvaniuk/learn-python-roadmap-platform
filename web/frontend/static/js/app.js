let currentModule = null;
let currentLesson = null;
let editor = null;
let lastErrorLine = null;
let currentExampleCode = "";

// Таймер
let timerInterval = null;
let lessonStartTime = null;
let sessionSeconds = 0;

const state = {
    token: localStorage.getItem("token"),
    user: JSON.parse(localStorage.getItem("user") || "null"),
    completed: [],
    total: 0,
    currentLevel: "junior",
    levelsData: null,
    byLevel: {},
    hints: [],
    hintIndex: 0,
    lessonMeta: null,
    theme: localStorage.getItem("learn_python_theme") || "dark",
    streak: parseInt(localStorage.getItem("learn_python_streak") || "0"),
    lastActivityDate: localStorage.getItem("learn_python_last_date") || "",
    running: false,
};

function authHeaders() {
    const h = { "Content-Type": "application/json" };
    if (state.token) h["Authorization"] = `Bearer ${state.token}`;
    return h;
}

async function init() {
    applyTheme(state.theme);
    updateAuthUI();
    setProgressLoading(true);
    await loadProgress();
    setProgressLoading(false);
    updateProgress();
    updateStreak();
    await loadModules();
    refreshLessonIndicators();
    initLevelTabs();
    initTabs();
    initEditor();
    initButtons();
    initHints();
    initThemeToggle();
    initSearch();
    initExport();
    initFullscreen();
    initNotes();
    initFormat();
    initLoadExample();
    initBeforeUnload();
}

function initLevelTabs() {
    document.querySelectorAll(".level-tab").forEach((tab) => {
        tab.onclick = async () => {
            await saveDraft();
            state.currentLevel = tab.dataset.level;
            document.querySelectorAll(".level-tab").forEach((t) => t.classList.remove("active"));
            tab.classList.add("active");
            loadModules().then(refreshLessonIndicators);
            currentModule = null;
            currentLesson = null;
            document.getElementById("lesson-title").textContent = "Оберіть урок";
        };
    });
}

function updateAuthUI() {
    const nameEl = document.getElementById("user-name");
    const loginBtn = document.getElementById("btn-login");
    const logoutBtn = document.getElementById("btn-logout");
    if (state.user) {
        nameEl.textContent = state.user.username || state.user.email;
        loginBtn.style.display = "none";
        logoutBtn.style.display = "block";
    } else {
        nameEl.textContent = "";
        loginBtn.style.display = "block";
        logoutBtn.style.display = "none";
    }
}

document.getElementById("btn-logout")?.addEventListener("click", async () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    state.token = null;
    state.user = null;
    state.completed = [];
    updateAuthUI();
    await loadProgress();
    refreshLessonIndicators();
    updateProgress();
});

async function loadProgress() {
    if (state.token) {
        try {
            const res = await fetch("/api/progress", { headers: authHeaders() });
            const data = await res.json();
            state.completed = data.completed || [];
            state.total = data.total || 23;
            state.byLevel = data.by_level || {};
        } catch {
            state.completed = [];
            state.byLevel = {};
        }
    } else {
        state.completed = JSON.parse(localStorage.getItem("learn_python_completed") || "[]");
        try {
            const res = await fetch("/api/progress");
            const data = await res.json();
            state.total = data.total || 0;
            state.byLevel = {};
        } catch {
            state.total = 0;
            state.byLevel = {};
        }
    }
}

function setProgressLoading(loading) {
    const el = document.getElementById("progress");
    if (el) el.textContent = loading ? "Завантаження…" : "";
}

function refreshLessonIndicators() {
    document.querySelectorAll(".lesson-item").forEach((a) => {
        const key = a.dataset.lessonKey;
        if (!key) return;
        a.classList.toggle("completed", state.completed.includes(key));
    });
}

async function loadModules() {
    const res = await fetch("/api/levels");
    state.levelsData = await res.json();
    const nav = document.getElementById("modules-nav");
    nav.innerHTML = "";
    const levelData = state.levelsData[state.currentLevel];
    if (!levelData) return;

    for (const mod of levelData.modules) {
        const modRes = await fetch(`/api/lessons/${mod.id}`);
        const modData = await modRes.json();

        const btn = document.createElement("button");
        btn.className = "module-btn";
        btn.textContent = modData.module;
        btn.onclick = (e) => toggleModule(mod.id, modData, e.currentTarget);

        const list = document.createElement("div");
        list.className = "lesson-list";
        list.id = `lessons-${mod.id}`;

        modData.lessons.forEach((l) => {
            const a = document.createElement("a");
            a.className = "lesson-item";
            a.href = "#";
            a.dataset.lessonKey = `${mod.id}/${l.id}`;
            a.innerHTML = `<span class="lesson-check"></span>${l.title}`;
            a.onclick = (e) => {
                e.preventDefault();
                loadLesson(mod.id, l.id, l.title);
            };
            list.appendChild(a);
        });

        nav.appendChild(btn);
        nav.appendChild(list);
    }
}

function toggleModule(moduleId, modData, clickedBtn) {
    document.querySelectorAll(".module-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".lesson-list").forEach((l) => l.classList.remove("open"));

    clickedBtn.classList.add("active");
    document.getElementById(`lessons-${moduleId}`).classList.add("open");
}

async function saveDraft() {
    if (!currentModule || !currentLesson || !editor) return;
    const code = editor.getValue();
    localStorage.setItem(`learn_python_draft_${currentModule}/${currentLesson}`, code);
    if (state.token) {
        try {
            const res = await fetch("/api/code", {
                method: "POST",
                headers: authHeaders(),
                body: JSON.stringify({ module_id: currentModule, lesson_id: currentLesson, code }),
            });
            if (res.ok) showSaveIndicator();
        } catch {
            // Fallback: localStorage вже збережено
        }
    }
}

function showSaveIndicator() {
    const el = document.getElementById("save-indicator");
    if (!el) return;
    el.textContent = "✓ Збережено";
    el.classList.add("visible");
    setTimeout(() => el.classList.remove("visible"), 2000);
}

function loadDraft(moduleId, lessonId) {
    return localStorage.getItem(`learn_python_draft_${moduleId}/${lessonId}`);
}

async function loadDraftFromApi(moduleId, lessonId) {
    if (!state.token) return null;
    try {
        const res = await fetch(`/api/code?module_id=${encodeURIComponent(moduleId)}&lesson_id=${encodeURIComponent(lessonId)}`, {
            headers: authHeaders(),
        });
        const data = await res.json();
        return data.code || null;
    } catch {
        return null;
    }
}

async function loadLesson(moduleId, lessonId, title) {
    await flushTimer();
    await saveDraft();
    currentModule = moduleId;
    currentLesson = lessonId;
    startTimer();

    document.querySelectorAll(".lesson-item").forEach((a) => a.classList.remove("active"));
    const activeItem = document.querySelector(`.lesson-item[data-lesson-key="${moduleId}/${lessonId}"]`);
    if (activeItem) activeItem.classList.add("active");

    document.getElementById("lesson-title").textContent = title;

    const res = await fetch(`/api/lessons/${moduleId}/${lessonId}`);
    const data = await res.json();

    state.hints = data.hints || [];
    state.hintIndex = 0;
    state.lessonMeta = data.meta || {};
    document.getElementById("solution-panel").style.display = "none";

    const metaEl = document.getElementById("lesson-meta");
    if (state.lessonMeta.difficulty || state.lessonMeta.time) {
        const diff = { easy: "🟢 Легко", medium: "🟡 Середньо", hard: "🔴 Складно" }[state.lessonMeta.difficulty] || "";
        metaEl.innerHTML = `${diff} ${state.lessonMeta.time || ""}`.trim();
        metaEl.style.display = "";
    } else {
        metaEl.style.display = "none";
    }

    marked.setOptions({ breaks: true });
    let theoryHtml = marked.parse(data.theory || "*Немає контенту*");
    if (data.resources?.length) {
        theoryHtml += '<div class="lesson-resources"><h4>Додаткові ресурси</h4><ul>' +
            data.resources.map((r) => `<li><a href="${r.url}" target="_blank" rel="noopener">${r.name}</a></li>`).join("") +
            "</ul></div>";
    }
    document.getElementById("theory-content").innerHTML = theoryHtml;
    document.getElementById("task-content").innerHTML = marked.parse(data.task || "*Немає завдань*");
    currentExampleCode = data.example || "";
    document.getElementById("example-code").textContent = currentExampleCode;

    const defaultCode = getDefaultCode(lessonId);
    const savedFromApi = await loadDraftFromApi(moduleId, lessonId);
    const savedLocal = loadDraft(moduleId, lessonId);
    editor.setValue(savedFromApi || savedLocal || defaultCode);

    updateProgress();
    await loadNote(moduleId, lessonId);
}

function getSolutionPath(moduleId, lessonId) {
    const map = {
        lesson_01_hello: "task_01",
        lesson_02_types: "task_02",
        lesson_03_flow: "task_03",
        lesson_04_functions: "task_04",
        lesson_01_lists: "task_ds_01",
        lesson_02_dicts_sets: "task_ds_02",
        lesson_03_comprehensions: "task_ds_03",
    };
    const file = map[lessonId] || "task";
    const base = moduleId.startsWith("02_") ? "02_middle" : moduleId.startsWith("03_") ? "03_senior" : `01_junior/${moduleId}`;
    return `${base}/solutions/${file}.py`;
}

function getDefaultCode(lessonId) {
    const defaults = {
        lesson_01_hello: '# Завдання 1: виведи "Я вивчаю Python", "Це мій перший урок", свій вік\n# Завдання 2: змінна city, виведи "Я живу в [місто]"\n# Завдання 3: a=10, b=3, виведи суму\n\n',
        lesson_02_types: '# Завдання з типів та операцій\n',
        lesson_03_flow: '# Умови та цикли\n',
        lesson_04_functions: '# Функції\n',
        lesson_01_lists: '# Списки та кортежі\n',
        lesson_02_dicts_sets: '# Словники та множини\n',
        lesson_03_comprehensions: '# Comprehensions\n',
        lesson_01_oop_advanced: '# Магічні методи, декоратори, property\n',
        lesson_02_async: '# asyncio, async/await\n',
        lesson_03_fastapi: '# FastAPI, REST API\n',
        lesson_04_databases: '# SQLAlchemy, ORM\n',
        lesson_05_testing: '# pytest\n',
        lesson_06_devops: '# Docker, Git\n',
        lesson_01_architecture: '# SOLID, архітектура\n',
        lesson_02_design_patterns: '# Design Patterns\n',
        lesson_03_system_design: '# Системний дизайн\n',
        lesson_04_code_quality: '# mypy, ruff, black\n',
        lesson_05_security: '# OWASP, безпека\n',
        lesson_06_soft_skills: '# Менторинг, code review\n',
    };
    return defaults[lessonId] || "# Напиши свій код тут\n";
}

function initTabs() {
    document.querySelectorAll(".tab").forEach((tab) => {
        tab.onclick = () => {
            document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
            tab.classList.add("active");
            document.getElementById(tab.dataset.tab).classList.add("active");
        };
    });
}

function initEditor() {
    const ta = document.getElementById("code-editor");
    const theme = state.theme === "light" ? "default" : "darcula";
    editor = CodeMirror.fromTextArea(ta, {
        mode: "python",
        theme: theme,
        lineNumbers: true,
        indentUnit: 4,
        tabSize: 4,
    });
    let saveTimeout;
    editor.on("change", () => {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(saveDraft, 500);
        clearErrorHighlight();
    });
    editor.setOption("extraKeys", {
        "Ctrl-Enter": runCode,
        "Cmd-Enter": runCode,
        "Ctrl-Shift-Enter": checkCode,
        "Cmd-Shift-Enter": checkCode,
    });
}

function setRunning(isRunning) {
    state.running = isRunning;
    const btnRun = document.getElementById("btn-run");
    const btnCheck = document.getElementById("btn-check");
    if (btnRun) {
        btnRun.disabled = isRunning;
        btnRun.textContent = isRunning ? "Виконується…" : "Запустити";
    }
    if (btnCheck) {
        btnCheck.disabled = isRunning;
        btnCheck.textContent = isRunning ? "Перевіряється…" : "Перевірити";
    }
}

function initButtons() {
    document.getElementById("btn-run").onclick = runCode;
    document.getElementById("btn-check").onclick = checkCode;
}

function initHints() {
    document.getElementById("btn-hint")?.addEventListener("click", showHint);
    document.getElementById("hint-close")?.addEventListener("click", () => {
        document.getElementById("hint-modal").style.display = "none";
    });
}

function showHint() {
    if (!state.hints.length) {
        alert("Підказок немає для цього уроку");
        return;
    }
    const text = state.hints[state.hintIndex] || state.hints[0];
    document.getElementById("hint-text").textContent = text;
    document.getElementById("hint-modal").style.display = "flex";
    if (state.hintIndex < state.hints.length - 1) state.hintIndex++;
}

function initThemeToggle() {
    document.getElementById("btn-theme")?.addEventListener("click", () => {
        state.theme = state.theme === "dark" ? "light" : "dark";
        localStorage.setItem("learn_python_theme", state.theme);
        applyTheme(state.theme);
    });
}

function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    if (editor) {
        editor.setOption("theme", theme === "light" ? "default" : "darcula");
    }
}

function initSearch() {
    const input = document.getElementById("search-lessons");
    input?.addEventListener("input", () => {
        const q = input.value.toLowerCase().trim();
        document.querySelectorAll(".lesson-item").forEach((el) => {
            const text = el.textContent.toLowerCase();
            el.style.display = q ? (text.includes(q) ? "" : "none") : "";
        });
    });
}

function initExport() {
    document.getElementById("btn-export")?.addEventListener("click", () => {
        const data = {
            completed: state.completed,
            total: state.total,
            streak: state.streak,
            exportDate: new Date().toISOString(),
        };
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "learn_python_progress.json";
        a.click();
        URL.revokeObjectURL(a.href);
    });
}

function initFullscreen() {
    document.getElementById("btn-fullscreen")?.addEventListener("click", () => {
        const section = document.querySelector(".editor-section");
        if (!document.fullscreenElement) {
            section?.requestFullscreen?.();
        } else {
            document.exitFullscreen?.();
        }
    });

    const theoryBody = document.getElementById("lesson-body");
    const btnTheoryFs = document.getElementById("btn-theory-fullscreen");
    btnTheoryFs?.addEventListener("click", () => {
        theoryBody?.classList.toggle("fullscreen");
        btnTheoryFs.textContent = theoryBody?.classList.contains("fullscreen") ? "✕" : "⛶";
        btnTheoryFs.title = theoryBody?.classList.contains("fullscreen") ? "Вийти (Esc)" : "На весь екран";
    });
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && theoryBody?.classList.contains("fullscreen")) {
            theoryBody.classList.remove("fullscreen");
            btnTheoryFs.textContent = "⛶";
            btnTheoryFs.title = "На весь екран (Esc — вийти)";
        }
    });
}

function updateStreak() {
    state.streak = parseInt(localStorage.getItem("learn_python_streak") || "0");
    state.lastActivityDate = localStorage.getItem("learn_python_last_date") || "";
    const el = document.getElementById("streak");
    if (el) el.textContent = state.streak ? `🔥 ${state.streak}` : "";
}

async function showSolution() {
    if (!currentModule || !currentLesson) return;
    try {
        const res = await fetch(`/api/lessons/${currentModule}/${currentLesson}/solution`);
        const data = await res.json();
        const panel = document.getElementById("solution-panel");
        document.getElementById("solution-code").textContent = data.solution || "";
        panel.style.display = "block";
    } catch {
        // Solution not available
    }
}

function saveStreakOnComplete() {
    const today = new Date().toDateString();
    if (state.lastActivityDate === today) return;
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayStr = yesterday.toDateString();
    if (state.lastActivityDate === yesterdayStr) {
        state.streak = (state.streak || 0) + 1;
    } else {
        state.streak = 1;
    }
    state.lastActivityDate = today;
    localStorage.setItem("learn_python_streak", String(state.streak));
    localStorage.setItem("learn_python_last_date", state.lastActivityDate);
    const el = document.getElementById("streak");
    if (el) el.textContent = state.streak ? `🔥 ${state.streak}` : "";
}

function clearErrorHighlight() {
    if (editor && lastErrorLine != null) {
        editor.removeLineClass(lastErrorLine, "background", "error-line");
        lastErrorLine = null;
    }
}

function highlightErrorLine(lineNum) {
    clearErrorHighlight();
    if (!editor || !lineNum) return;
    const line = Math.max(0, parseInt(lineNum) || 1) - 1;
    if (line < editor.lineCount()) {
        editor.addLineClass(line, "background", "error-line");
        lastErrorLine = line;
        editor.getDoc().setCursor(line, 0);
    }
}

async function runCode() {
    if (state.running) return;
    clearErrorHighlight();
    const code = editor.getValue();
    const output = document.getElementById("output");
    output.className = "";
    setRunning(true);

    try {
        const res = await fetch("/api/run", {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify({ code }),
        });
        const data = await res.json();

        if (data.success) {
            output.textContent = data.output || "(порожній вивід)";
            if (data.error) output.textContent += "\n" + data.error;
        } else {
            output.className = "error";
            output.textContent = data.error || "Помилка виконання";
            const match = (data.error || "").match(/line (\d+)/i) || (data.error || "").match(/:(\d+)/);
            if (match) highlightErrorLine(match[1]);
        }
    } catch (err) {
        output.className = "error";
        output.textContent = "Мережева помилка: " + err.message;
    } finally {
        setRunning(false);
    }
}


async function checkCode() {
    if (state.running) return;
    if (!currentLesson) {
        alert("Оберіть урок");
        return;
    }

    const code = editor.getValue();
    const resultEl = document.getElementById("check-result");
    setRunning(true);

    try {
        const res = await fetch("/api/check", {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify({ lesson_id: currentLesson, code }),
        });
        const data = await res.json();

        resultEl.className = "check-result show " + (data.passed ? "passed" : "failed");
        // Безпечний вивід через textContent щоб уникнути XSS
        resultEl.innerHTML = "";
        const strong = document.createElement("strong");
        strong.textContent = data.message;
        resultEl.appendChild(strong);
        if (data.details?.length) {
            const ul = document.createElement("ul");
            data.details.forEach((d) => {
                const li = document.createElement("li");
                li.textContent = d;
                ul.appendChild(li);
            });
            resultEl.appendChild(ul);
        }

        if (data.passed) {
            const key = `${currentModule}/${currentLesson}`;
            if (!state.completed.includes(key)) {
                state.completed.push(key);
                saveStreakOnComplete();
                showSolution();
                if (state.token) {
                    try {
                        await fetch("/api/progress", {
                            method: "POST",
                            headers: authHeaders(),
                            body: JSON.stringify({
                                module_id: currentModule,
                                lesson_id: currentLesson,
                                time_spent: sessionSeconds,
                            }),
                        });
                        sessionSeconds = 0;
                    } catch {
                        localStorage.setItem("learn_python_completed", JSON.stringify(state.completed));
                    }
                } else {
                    localStorage.setItem("learn_python_completed", JSON.stringify(state.completed));
                }
                updateProgress();
            }
        }
    } catch (err) {
        resultEl.className = "check-result show failed";
        resultEl.textContent = "Мережева помилка: " + err.message;
    } finally {
        setRunning(false);
    }
}

const LEVEL_MODULES = { junior: ["01_basics", "02_data_structures", "03_oop", "04_files_errors"], middle: ["02_middle"], senior: ["03_senior"] };
const MODULE_LESSON_COUNT = { "01_basics": 4, "02_data_structures": 3, "03_oop": 2, "04_files_errors": 2, "02_middle": 6, "03_senior": 6 };

function getByLevel() {
    if (state.byLevel && Object.keys(state.byLevel).length) return state.byLevel;
    const byLevel = {};
    for (const [levelId, modules] of Object.entries(LEVEL_MODULES)) {
        let done = 0, total = 0;
        for (const mid of modules) {
            total += MODULE_LESSON_COUNT[mid] || 0;
            done += state.completed.filter((k) => k.startsWith(mid + "/")).length;
        }
        byLevel[levelId] = { done, total };
    }
    return byLevel;
}

const ACHIEVEMENTS = [
    { count: 1, badge: "🌟", name: "Перший урок" },
    { count: 5, badge: "📚", name: "5 уроків" },
    { count: 10, badge: "🚀", name: "10 уроків" },
    { count: 11, badge: "🎓", name: "Junior завершено" },
    { count: 23, badge: "🏆", name: "Курс завершено" },
];

function updateProgress() {
    const total = state.total || 0;
    const done = state.completed.length;
    const el = document.getElementById("progress");
    if (!el) return;
    const byLevel = getByLevel();
    const levelNames = { junior: "J", middle: "M", senior: "S" };
    const parts = Object.entries(byLevel).map(([k, v]) => v.total ? `${levelNames[k] || k}: ${v.done}/${v.total}` : null).filter(Boolean);
    let text = parts.length ? `Прогрес: ${done}/${total} (${parts.join(", ")})` : `Прогрес: ${done}/${total} уроків`;
    const achieved = ACHIEVEMENTS.filter((a) => done >= a.count).map((a) => a.badge).join(" ");
    if (achieved) text += " " + achieved;
    el.textContent = text;
}

// ── Таймер ────────────────────────────────────────────────────
function startTimer() {
    stopTimer();
    lessonStartTime = Date.now();
    sessionSeconds = 0;
    const el = document.getElementById("lesson-timer");
    if (el) el.style.display = "";
    timerInterval = setInterval(() => {
        sessionSeconds = Math.floor((Date.now() - lessonStartTime) / 1000);
        const m = String(Math.floor(sessionSeconds / 60)).padStart(2, "0");
        const s = String(sessionSeconds % 60).padStart(2, "0");
        if (el) el.textContent = `⏱ ${m}:${s}`;
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

async function flushTimer() {
    if (!currentModule || !currentLesson || sessionSeconds < 5) return;
    const secs = sessionSeconds;
    sessionSeconds = 0;
    if (state.token) {
        try {
            await fetch("/api/time", {
                method: "POST",
                headers: authHeaders(),
                body: JSON.stringify({ module_id: currentModule, lesson_id: currentLesson, seconds: secs }),
            });
        } catch {
            // ігноруємо
        }
    }
}

// ── Нотатки ───────────────────────────────────────────────────
let noteSaveTimeout = null;

function initNotes() {
    const ta = document.getElementById("note-editor");
    if (!ta) return;
    ta.addEventListener("input", () => {
        clearTimeout(noteSaveTimeout);
        noteSaveTimeout = setTimeout(saveNote, 800);
    });
}

async function loadNote(moduleId, lessonId) {
    const ta = document.getElementById("note-editor");
    if (!ta) return;
    ta.value = "";
    if (!state.token) return;
    try {
        const res = await fetch(
            `/api/notes?module_id=${encodeURIComponent(moduleId)}&lesson_id=${encodeURIComponent(lessonId)}`,
            { headers: authHeaders() }
        );
        const data = await res.json();
        ta.value = data.content || "";
    } catch {
        // offline — нічого
    }
}

async function saveNote() {
    if (!currentModule || !currentLesson || !state.token) return;
    const ta = document.getElementById("note-editor");
    if (!ta) return;
    const indicator = document.getElementById("note-save-indicator");
    try {
        await fetch("/api/notes", {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify({ module_id: currentModule, lesson_id: currentLesson, content: ta.value }),
        });
        if (indicator) {
            indicator.textContent = "✓ Збережено";
            indicator.classList.add("visible");
            setTimeout(() => indicator.classList.remove("visible"), 2000);
        }
    } catch {
        // offline
    }
}

// ── Форматування коду (black) ──────────────────────────────────
function initFormat() {
    document.getElementById("btn-format")?.addEventListener("click", formatCode);
}

async function formatCode() {
    if (!editor) return;
    const code = editor.getValue();
    if (!code.trim()) return;
    const btn = document.getElementById("btn-format");
    if (btn) btn.textContent = "…";
    try {
        const res = await fetch("/api/format", {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify({ code }),
        });
        const data = await res.json();
        if (data.success) {
            editor.setValue(data.code);
            if (btn) btn.textContent = "✓ Format";
            setTimeout(() => { if (btn) btn.textContent = "⚡ Format"; }, 1500);
        } else {
            if (btn) btn.textContent = "⚡ Format";
            const output = document.getElementById("output");
            if (output) { output.className = "error"; output.textContent = data.error || "Помилка форматування"; }
        }
    } catch {
        if (btn) btn.textContent = "⚡ Format";
    }
}

// ── Завантажити приклад у редактор ─────────────────────────────
function initLoadExample() {
    document.getElementById("btn-load-example")?.addEventListener("click", () => {
        if (!editor || !currentExampleCode) return;
        if (confirm("Замінити код у редакторі прикладом?")) {
            editor.setValue(currentExampleCode);
            // Перемикаємося на редактор
            document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
        }
    });
}

// ── Зберегти час при закритті сторінки ─────────────────────────
function initBeforeUnload() {
    window.addEventListener("beforeunload", () => {
        if (currentModule && currentLesson && sessionSeconds >= 5 && state.token) {
            navigator.sendBeacon(
                "/api/time",
                JSON.stringify({ module_id: currentModule, lesson_id: currentLesson, seconds: sessionSeconds })
            );
        }
    });
}

document.addEventListener("DOMContentLoaded", init);
