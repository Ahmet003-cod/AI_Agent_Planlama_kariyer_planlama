document.addEventListener("DOMContentLoaded", () => {
    // State management
    const state = {
        career_goal: "",
        roadmaps: {}, // { career_goal: { Adimlar: [...] } }
        schedules: {}, // { step_name: { "1": { HaftalikPlan }, "2": { HaftalikPlan } } }
        reminders: [], // [ { id, step, week, day, taskIndex, text, time, message, status: 'pending'/'fired' } ]
        completed_steps: [], // list of step titles/names
        completed_tasks: {}, // { step_title: [task_text_1, task_text_2] }
        chat_histories: {}, // { domain_name: [ { role: 'user/assistant', content: '...' } ] }
        active_step_for_scheduler: "",
        active_step_for_suggestions: "",
        active_step_for_details: null,
        active_chat_domain: "offensive",
        active_week: 1,
        edit_mode: false
    };

    // Active modal reminder data state
    let activeReminderTask = null;

    // DOM Elements
    const elements = {
        navItems: document.querySelectorAll(".nav-item"),
        pages: document.querySelectorAll(".app-page"),
        careerInput: document.getElementById("career-input"),
        btnGenerateRoadmap: document.getElementById("btn-generate-roadmap"),
        quickTags: document.querySelectorAll(".quick-tag-btn"),
        navScheduler: document.getElementById("nav-scheduler"),
        navSimulation: document.getElementById("nav-simulation"),
        
        // Roadmap Page
        roadmapEmpty: document.getElementById("roadmap-empty"),
        roadmapVisualFlowArea: document.getElementById("roadmap-visual-flow-area"),
        roadmapDetailsCardArea: document.getElementById("roadmap-details-card-area"),
        detailStepBadge: document.getElementById("detail-step-badge"),
        detailStepTitle: document.getElementById("detail-step-title"),
        detailStepProgressText: document.getElementById("detail-step-progress-text"),
        detailStepProgressBar: document.getElementById("detail-step-progress-bar"),
        detailStepDescription: document.getElementById("detail-step-description"),
        detailStepTasksList: document.getElementById("detail-step-tasks-list"),
        detailStepVideosList: document.getElementById("detail-step-videos-list"),
        detailStepDocsList: document.getElementById("detail-step-docs-list"),
        btnDetailGetSchedule: document.getElementById("btn-detail-get-schedule"),

        // Chat Page
        expertCards: document.querySelectorAll(".expert-card"),
        chatMessagesArea: document.getElementById("chat-messages-area"),
        chatUserInput: document.getElementById("chat-user-input"),
        btnSendMessage: document.getElementById("btn-send-message"),
        btnClearChat: document.getElementById("btn-clear-chat"),
        activeExpertTitle: document.getElementById("active-expert-title"),

        // Scheduler Page
        schedulerEmpty: document.getElementById("scheduler-empty"),
        schedulerContent: document.getElementById("scheduler-content"),
        schedulerStepTitle: document.getElementById("scheduler-step-title"),
        schedulerWeekTabs: document.getElementById("scheduler-week-tabs"),
        btnPlanNextWeek: document.getElementById("btn-plan-next-week"),
        btnToggleEditMode: document.getElementById("btn-toggle-edit-mode"),
        weeklyPlannerGrid: document.getElementById("weekly-planner-grid"),
        
        // Suggestions Page
        suggestionsEmpty: document.getElementById("suggestions-empty"),
        suggestionsContent: document.getElementById("suggestions-content"),
        suggestionsStepTitle: document.getElementById("suggestions-step-title"),

        // Simulation Page
        simulationEmpty: document.getElementById("simulation-empty"),
        simulationDashboardArea: document.getElementById("simulation-dashboard-area"),
        simulationProgressRing: document.getElementById("simulation-progress-ring"),
        simulationTimerText: document.getElementById("simulation-timer-text"),
        btnStartSimulation: document.getElementById("btn-start-simulation"),
        simulationConsoleLogArea: document.getElementById("simulation-console-log-area"),
        simulationRewardBadgeCard: document.getElementById("simulation-reward-badge-card"),
        simulationRewardTitle: document.getElementById("simulation-reward-title"),
        simulationRewardDesc: document.getElementById("simulation-reward-desc"),
        btnSimulationGoRoadmap: document.getElementById("btn-simulation-go-roadmap"),
        
        displayGoal: document.getElementById("display-goal"),
        loadingSpinner: document.getElementById("loading-spinner"),
        loadingText: document.getElementById("loading-text"),
        apiStatusText: document.getElementById("api-status-text"),
        apiStatusBadge: document.querySelector(".api-status-badge"),
        progressSection: document.getElementById("dashboard-progress-section"),
        progressBarFill: document.getElementById("progress-bar-fill"),
        progressPercentage: document.getElementById("progress-percentage"),
        progressStepsCount: document.getElementById("progress-steps-count"),

        // Reminders & Modal Elements
        reminderModal: document.getElementById("reminder-modal"),
        btnCloseReminderModal: document.getElementById("btn-close-reminder-modal"),
        reminderTaskText: document.getElementById("reminder-task-text"),
        reminderDatetime: document.getElementById("reminder-datetime"),
        reminderMessage: document.getElementById("reminder-message"),
        btnCancelReminder: document.getElementById("btn-cancel-reminder"),
        btnSaveReminder: document.getElementById("btn-save-reminder"),
        toastNotificationsArea: document.getElementById("toast-notifications-area")
    };

    // Initialize Page Navigation
    elements.navItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            if (item.classList.contains("disabled-nav")) return;
            const targetHash = item.getAttribute("href");
            switchPage(targetHash);
        });
    });

    function switchPage(hash) {
        elements.navItems.forEach(nav => nav.classList.remove("active"));
        const activeNav = document.querySelector(`.nav-item[href="${hash}"]`);
        if (activeNav) activeNav.classList.add("active");

        elements.pages.forEach(page => page.classList.remove("active"));
        const targetPageId = "page-" + hash.replace("#", "");
        const targetPage = document.getElementById(targetPageId);
        if (targetPage) targetPage.classList.add("active");

        const titleEl = document.getElementById("page-title");
        const subtitleEl = document.getElementById("page-subtitle");
        
        if (hash === "#dashboard") {
            titleEl.textContent = "Siber Güvenlik Kariyer Paneli";
            subtitleEl.textContent = "Yapay zeka destekli siber güvenlik yolculuğunuzu başlatın.";
        } else if (hash === "#chat") {
            titleEl.textContent = "Siber Güvenlik Uzman Sohbeti";
            subtitleEl.textContent = "Kırmızı, Mavi veya Adli Bilişim siber güvenlik ajanlarıyla konuşun.";
        } else if (hash === "#roadmap") {
            titleEl.textContent = "Uzmanlık Yol Haritası";
            subtitleEl.textContent = "Hedeflerinize ulaşmak için siber güvenlikte izlemeniz gereken adımlar.";
        } else if (hash === "#scheduler") {
            titleEl.textContent = "Çalışma Programı";
            subtitleEl.textContent = "Adım bazında planlanmış haftalık görevleriniz.";
        } else if (hash === "#suggestions") {
            titleEl.textContent = "Kaynak Önerileri";
            subtitleEl.textContent = "Seçtiğiniz siber güvenlik adımına göre toplanan kaynaklar.";
            if (state.active_step_for_scheduler) {
                loadSuggestions(state.active_step_for_scheduler);
            }
        } else if (hash === "#simulation") {
            titleEl.textContent = "Siber Simülatör";
            subtitleEl.textContent = "15 saniyelik motivasyon kapsülüyle geleceğini deneyimle.";
            initSimulationUI();
        }
    }

    // Quick Tag Buttons
    elements.quickTags.forEach(btn => {
        btn.addEventListener("click", () => {
            elements.careerInput.value = btn.textContent;
            elements.careerInput.focus();
        });
    });

    // Check API Status and load profile
    checkApiStatus();
    loadUserProfile();
    requestNotificationPermission();

    // Alarm Timer Loop (Every 5 seconds)
    setInterval(checkAlarms, 5000);

    // Browser Notification Request Permission
    function requestNotificationPermission() {
        if ("Notification" in window && Notification.permission !== "granted" && Notification.permission !== "denied") {
            Notification.requestPermission();
        }
    }

    // Alarm Checker Function
    function checkAlarms() {
        if (!state.reminders || state.reminders.length === 0) return;
        const now = new Date();

        state.reminders.forEach(async reminder => {
            if (reminder.status === "pending") {
                const alarmTime = new Date(reminder.time);
                if (alarmTime <= now) {
                    reminder.status = "fired";
                    await saveUserProfile();

                    if ("Notification" in window && Notification.permission === "granted") {
                        try {
                            new Notification("CyberShield AI Alarmı!", {
                                body: `${reminder.text}\n\nNot: ${reminder.message}`,
                                icon: "/static/favicon.ico"
                            });
                        } catch (err) {
                            console.error("Browser notification failed", err);
                        }
                    }

                    showToast(`Zamanı Geldi: ${reminder.step}`, `${reminder.text}<br><strong>Not:</strong> ${reminder.message}`);
                    
                    if (state.active_step_for_scheduler === reminder.step) {
                        renderWeeklySchedule(reminder.step, state.active_week);
                    }
                }
            }
        });
    }

    // Toast Notification Builder
    function showToast(title, desc, duration = 8000) {
        const toast = document.createElement("div");
        toast.className = "toast-box";
        toast.innerHTML = `
            <div class="toast-icon"><i class="fa-solid fa-bell fa-shake"></i></div>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-desc">${desc}</div>
            </div>
            <button class="btn-close-toast"><i class="fa-solid fa-xmark"></i></button>
            <div class="toast-progress"></div>
        `;
        
        const closeBtn = toast.querySelector(".btn-close-toast");
        closeBtn.onclick = () => {
            toast.style.opacity = "0";
            setTimeout(() => toast.remove(), 300);
        };

        elements.toastNotificationsArea.appendChild(toast);

        const progressBar = toast.querySelector(".toast-progress");
        progressBar.style.width = "100%";
        setTimeout(() => {
            progressBar.style.transition = `width ${duration}ms linear`;
            progressBar.style.width = "0%";
        }, 50);

        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.opacity = "0";
                setTimeout(() => toast.remove(), 300);
            }
        }, duration);
    }

    // Modal Control Handlers
    elements.btnCloseReminderModal.onclick = closeReminderModal;
    elements.btnCancelReminder.onclick = closeReminderModal;
    
    function closeReminderModal() {
        elements.reminderModal.style.display = "none";
        activeReminderTask = null;
    }

    elements.btnSaveReminder.onclick = async () => {
        const datetimeVal = elements.reminderDatetime.value;
        const msgVal = elements.reminderMessage.value.trim();

        if (!datetimeVal) {
            alert("Lütfen geçerli bir tarih ve saat seçin!");
            return;
        }

        if (activeReminderTask) {
            const reminder = {
                id: "rem-" + Date.now(),
                step: activeReminderTask.step,
                week: activeReminderTask.week,
                day: activeReminderTask.day,
                taskIndex: activeReminderTask.taskIndex,
                text: activeReminderTask.text,
                time: datetimeVal,
                message: msgVal || "Siber çalışma vakti geldi!",
                status: "pending"
            };

            state.reminders.push(reminder);
            await saveUserProfile();
            showToast("Hatırlatıcı Ayarlandı", `"${activeReminderTask.text}" görevi için başarıyla alarm kuruldu.`);
            
            renderWeeklySchedule(activeReminderTask.step, state.active_week);
            closeReminderModal();
        }
    };

    // API Status Checker
    async function checkApiStatus() {
        try {
            const res = await fetch("/api/profile");
            if (res.ok) {
                elements.apiStatusBadge.classList.add("online");
                elements.apiStatusBadge.classList.remove("offline");
                elements.apiStatusText.textContent = "Ajan Bağlantısı Aktif";
            }
        } catch {
            elements.apiStatusBadge.classList.add("offline");
            elements.apiStatusBadge.classList.remove("online");
            elements.apiStatusText.textContent = "Çevrimdışı Mod";
        }
    }

    // Load User Profile
    async function loadUserProfile() {
        showLoading("Siber profil yükleniyor...");
        try {
            const response = await fetch("/api/profile");
            if (response.ok) {
                const data = await response.json();
                state.career_goal = data.career_goal || "";
                state.roadmaps = data.roadmaps || {};
                state.reminders = data.reminders || [];
                state.completed_steps = data.completed_steps || [];
                state.completed_tasks = data.completed_tasks || {};
                state.chat_histories = data.chat_histories || {};

                if (data.schedules) {
                    state.schedules = {};
                    for (let key in data.schedules) {
                        let val = data.schedules[key];
                        if (val && val.HaftalikPlan) {
                            state.schedules[key] = { "1": val };
                        } else {
                            state.schedules[key] = val;
                        }
                    }
                }

                if (state.career_goal) {
                    elements.displayGoal.textContent = state.career_goal;
                    elements.careerInput.value = state.career_goal;
                    elements.navScheduler.classList.remove("disabled-nav");
                    updateDashboardStats();
                    renderRoadmap();
                } else {
                    elements.navScheduler.classList.add("disabled-nav");
                }
            }
        } catch (error) {
            console.error("Profil yüklenemedi:", error);
        } finally {
            hideLoading();
        }
    }

    // Save User Profile
    async function saveUserProfile() {
        try {
            await fetch("/api/profile", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    career_goal: state.career_goal,
                    roadmaps: state.roadmaps,
                    schedules: state.schedules,
                    reminders: state.reminders,
                    completed_steps: state.completed_steps,
                    completed_tasks: state.completed_tasks,
                    chat_histories: state.chat_histories
                })
            });
            updateDashboardStats();
        } catch (error) {
            console.error("Profil kaydedilemedi:", error);
        }
    }

    // Update stats
    function updateDashboardStats() {
        const activeRoadmap = state.roadmaps[state.career_goal];
        if (activeRoadmap && activeRoadmap.Adimlar && activeRoadmap.Adimlar.length > 0) {
            const totalSteps = activeRoadmap.Adimlar.length;
            const completedCount = activeRoadmap.Adimlar.filter(stepObj => {
                const stepTitle = typeof stepObj === 'string' ? stepObj : stepObj.Baslik;
                return state.completed_steps.includes(stepTitle);
            }).length;

            const percentage = Math.round((completedCount / totalSteps) * 100);
            elements.progressSection.style.display = "grid";
            elements.progressBarFill.style.width = `${percentage}%`;
            elements.progressPercentage.textContent = `${percentage}%`;
            elements.progressStepsCount.textContent = `${completedCount} / ${totalSteps}`;
        } else {
            elements.progressSection.style.display = "none";
        }
    }

    // Generate Roadmap
    elements.btnGenerateRoadmap.addEventListener("click", async () => {
        const goal = elements.careerInput.value.trim();
        if (!goal) {
            alert("Lütfen bir siber güvenlik hedefi girin!");
            return;
        }

        showLoading("Siber Yol Haritası Çıkarılıyor...");
        try {
            const response = await fetch("/api/career-goal", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ career_goal: goal })
            });

            if (response.ok) {
                const data = await response.json();
                if (data.hata) {
                    alert("Hata: " + data.hata);
                } else {
                    state.career_goal = goal;
                    state.roadmaps[goal] = data;
                    state.schedules = {};
                    state.reminders = [];
                    state.completed_steps = [];
                    state.completed_tasks = {};
                    elements.displayGoal.textContent = goal;
                    
                    elements.navScheduler.classList.remove("disabled-nav");
                    
                    await saveUserProfile();
                    renderRoadmap();
                    
                    if (data.Adimlar && data.Adimlar.length > 0) {
                        const firstStep = data.Adimlar[0];
                        const firstStepTitle = typeof firstStep === 'string' ? firstStep : firstStep.Baslik;
                        state.active_step_for_scheduler = firstStepTitle;
                        state.active_week = 1;
                        await loadWeeklySchedule(firstStepTitle, true, 1);
                    }
                    
                    switchPage("#roadmap");
                }
            } else {
                alert("Yol haritası oluşturulamadı.");
            }
        } catch (error) {
            alert("Sunucuyla bağlantı kurulamadı.");
            console.error(error);
        } finally {
            hideLoading();
        }
    });

    // Render roadmap
    function renderRoadmap() {
        const activeRoadmap = state.roadmaps[state.career_goal];
        if (!activeRoadmap || !activeRoadmap.Adimlar || activeRoadmap.Adimlar.length === 0) {
            elements.roadmapEmpty.style.display = "flex";
            elements.roadmapVisualFlowArea.style.display = "none";
            elements.roadmapDetailsCardArea.style.display = "none";
            return;
        }

        elements.roadmapEmpty.style.display = "none";
        elements.roadmapVisualFlowArea.innerHTML = "";
        elements.roadmapVisualFlowArea.style.display = "flex";

        let defaultStepObj = activeRoadmap.Adimlar[0];
        let foundActive = false;
        
        activeRoadmap.Adimlar.forEach((stepObj, index) => {
            const step = typeof stepObj === 'string' ? {
                AdimNo: index + 1,
                Baslik: stepObj,
                Aciklama: "Bu adım hakkında detaylı bilgi almak için tıklayın.",
                Gorevler: [
                    "Temel siber kavramları ve standartları araştırın.",
                    "Uygulamalı siber laboratuvar (lab) egzersizleri yapın.",
                    "Konuyla ilgili teknik bir senaryo çözün."
                ],
                Kaynaklar: []
            } : stepObj;

            const isCompleted = state.completed_steps.includes(step.Baslik);
            
            if (state.active_step_for_details && state.active_step_for_details.Baslik === step.Baslik) {
                defaultStepObj = step;
                foundActive = true;
            }

            const nodeDiv = document.createElement("div");
            nodeDiv.className = `roadmap-node ${isCompleted ? 'completed' : ''} ${state.active_step_for_details && state.active_step_for_details.Baslik === step.Baslik ? 'active-node' : ''}`;
            nodeDiv.innerHTML = `
                <div class="node-circle">${step.AdimNo || (index + 1)}</div>
                <div class="node-card">
                    <h4>${step.Baslik}</h4>
                    <p>${step.Aciklama || ''}</p>
                </div>
            `;

            nodeDiv.addEventListener("click", () => {
                state.active_step_for_details = step;
                state.active_step_for_scheduler = step.Baslik;
                state.active_week = 1;
                
                document.querySelectorAll(".roadmap-node").forEach(n => n.classList.remove("active-node"));
                nodeDiv.classList.add("active-node");
                
                renderStepDetails(step);
                loadWeeklySchedule(step.Baslik, true, 1);
            });

            elements.roadmapVisualFlowArea.appendChild(nodeDiv);
        });

        if (state.active_step_for_details && foundActive) {
            renderStepDetails(state.active_step_for_details);
            loadWeeklySchedule(state.active_step_for_details.Baslik, true, 1);
        } else {
            const normalizedDefault = typeof defaultStepObj === 'string' ? {
                AdimNo: 1,
                Baslik: defaultStepObj,
                Aciklama: "Bu adım hakkında detaylı bilgi almak için tıklayın.",
                Gorevler: [
                    "Temel kavramları ve terminolojiyi araştırın.",
                    "Uygulamalı egzersizler ve pratikler yapın.",
                    "Konuyla ilgili ufak bir senaryo çözün."
                ],
                Kaynaklar: []
            } : defaultStepObj;
            state.active_step_for_details = normalizedDefault;
            state.active_step_for_scheduler = normalizedDefault.Baslik;
            state.active_week = 1;
            
            const firstNode = elements.roadmapVisualFlowArea.querySelector(".roadmap-node");
            if (firstNode) firstNode.classList.add("active-node");
            
            renderStepDetails(normalizedDefault);
            loadWeeklySchedule(normalizedDefault.Baslik, true, 1);
        }
    }

    // Render Step Details Sidebar Card
    function renderStepDetails(step) {
        elements.roadmapDetailsCardArea.style.display = "flex";

        elements.detailStepBadge.textContent = `ADIM ${step.AdimNo || 1}`;
        elements.detailStepTitle.textContent = step.Baslik;
        elements.detailStepDescription.textContent = step.Aciklama || "Açıklama bulunmuyor.";

        elements.detailStepTasksList.innerHTML = "";
        const tasks = step.Gorevler || [];
        const completedTasksList = state.completed_tasks[step.Baslik] || [];
        
        let completedCount = 0;
        
        tasks.forEach((task, tIndex) => {
            const isChecked = completedTasksList.includes(task);
            if (isChecked) completedCount++;

            const taskItem = document.createElement("div");
            taskItem.className = `detail-task-item ${isChecked ? 'checked' : ''}`;
            taskItem.innerHTML = `
                <input type="checkbox" id="task-${tIndex}" ${isChecked ? 'checked' : ''}>
                <span>${task}</span>
            `;

            const checkbox = taskItem.querySelector("input");
            checkbox.addEventListener("change", async () => {
                let currentCompleted = state.completed_tasks[step.Baslik] || [];
                if (checkbox.checked) {
                    if (!currentCompleted.includes(task)) currentCompleted.push(task);
                    taskItem.classList.add("checked");
                } else {
                    const idx = currentCompleted.indexOf(task);
                    if (idx > -1) currentCompleted.splice(idx, 1);
                    taskItem.classList.remove("checked");
                }
                state.completed_tasks[step.Baslik] = currentCompleted;

                const allDone = tasks.length > 0 && currentCompleted.length === tasks.length;
                const isStepCompleted = state.completed_steps.includes(step.Baslik);

                if (allDone && !isStepCompleted) {
                    state.completed_steps.push(step.Baslik);
                } else if (!allDone && isStepCompleted) {
                    const sIdx = state.completed_steps.indexOf(step.Baslik);
                    if (sIdx > -1) state.completed_steps.splice(sIdx, 1);
                }

                updateStepProgressUI(tasks, currentCompleted.length, step.Baslik);
                renderRoadmap();
                await saveUserProfile();
            });

            elements.detailStepTasksList.appendChild(taskItem);
        });

        updateStepProgressUI(tasks, completedCount, step.Baslik);

        elements.detailStepVideosList.innerHTML = "";
        elements.detailStepDocsList.innerHTML = "";
        
        const resources = step.Kaynaklar || [];
        let hasVideos = false;
        let hasDocs = false;

        resources.forEach(res => {
            const resCard = document.createElement("div");
            resCard.className = "resource-card";
            resCard.innerHTML = `
                <div class="resource-meta">
                    <span class="res-type-badge ${res.Tur.toLowerCase()}">${res.Tur}</span>
                </div>
                <h5>${res.Baslik}</h5>
                <p>${res.Aciklama || ''}</p>
                <a href="${res.Link}" target="_blank" class="btn-resource-link">
                    <span>Eğitime Git</span>
                    <i class="fa-solid fa-arrow-up-right-from-square"></i>
                </a>
            `;

            if (res.Tur.toLowerCase() === "video") {
                elements.detailStepVideosList.appendChild(resCard);
                hasVideos = true;
            } else {
                elements.detailStepDocsList.appendChild(resCard);
                hasDocs = true;
            }
        });

        if (!hasVideos) {
            elements.detailStepVideosList.innerHTML = `
                <div class="empty-state" style="padding: 1rem 0;">
                    <p style="font-size:0.75rem; color:var(--text-muted);">Bu adım için video ders bulunamadı.</p>
                </div>
            `;
        }
        if (!hasDocs) {
            elements.detailStepDocsList.innerHTML = `
                <div class="empty-state" style="padding: 1rem 0;">
                    <p style="font-size:0.75rem; color:var(--text-muted);">Bu adım için dokümantasyon kaynağı bulunamadı.</p>
                </div>
            `;
        }

        elements.btnDetailGetSchedule.onclick = async () => {
            state.active_step_for_scheduler = step.Baslik;
            state.active_week = 1;
            await loadWeeklySchedule(step.Baslik, false, 1);
            switchPage("#scheduler");
        };
    }

    function updateStepProgressUI(tasks, checkedCount, stepTitle) {
        const total = tasks.length;
        const percent = total > 0 ? Math.round((checkedCount / total) * 100) : 0;
        
        elements.detailStepProgressText.textContent = `Tamamlanma: ${checkedCount} / ${total}`;
        elements.detailStepProgressBar.style.width = `${percent}%`;
    }


    // --- CHAT EXPERT SECTION ---
    const welcomeMessages = {
        "offensive": "Merhaba! Ben Offensive Security (Kırmızı Takım) uzmanınızım. Sızma testleri, exploit geliştirme, web güvenliği ve siber saldırı simülasyonları hakkında dilediğinizi sorabilirsiniz.",
        "defensive": "Selamlar! Ben Defensive Security (Mavi Takım) uzmanınızım. SOC analizi, SIEM altyapısı, log analizi ve olay müdahale süreçleri hakkında sorularınızı yanıtlamak için buradayım.",
        "malware-forensics": "Merhaba! Ben Zararlı Yazılım Analizi ve Adli Bilişim uzmanınızım. Tersine mühendislik, statik/dinamik kod analizi, disk ve bellek analizi konularında rehberlik edebilirim.",
        "grc": "Merhaba! Ben GRC (Uyum ve Siber Risk) uzmanınızım. ISO 27001, KVKK/GDPR uyumluluğu, siber güvenlik politikaları ve risk analizi süreçleri hakkında görüşebiliriz.",
        "cloud-security": "Selamlar! Bulut Güvenliği uzmanınız burada. AWS, Azure, Google Cloud platformlarında güvenli mimari kurulumu ve konteyner (Docker/Kubernetes) güvenliği hakkında konuşabiliriz."
    };

    elements.expertCards.forEach(card => {
        card.addEventListener("click", () => {
            elements.expertCards.forEach(c => c.classList.remove("active"));
            card.classList.add("active");
            
            const domain = card.getAttribute("data-domain");
            state.active_chat_domain = domain;
            elements.activeExpertTitle.textContent = card.querySelector("h4").textContent;
            loadChatHistory(domain);
        });
    });

    function loadChatHistory(domain) {
        elements.chatMessagesArea.innerHTML = "";
        const history = state.chat_histories[domain] || [];
        
        if (history.length === 0) {
            const welcomeMsg = welcomeMessages[domain] || "Merhaba! Siber güvenlik kariyerinde sana nasıl yardımcı olabilirim?";
            appendMessage("assistant", welcomeMsg);
        } else {
            history.forEach(msg => {
                appendMessage(msg.role, msg.content);
            });
        }
        scrollToBottom();
    }

    elements.btnSendMessage.addEventListener("click", () => {
        handleUserSendMessage();
    });

    elements.chatUserInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            handleUserSendMessage();
        }
    });

    elements.btnClearChat.addEventListener("click", async () => {
        if (confirm("Bu uzmanla olan sohbet geçmişinizi sıfırlamak istiyor musunuz?")) {
            state.chat_histories[state.active_chat_domain] = [];
            await saveUserProfile();
            loadChatHistory(state.active_chat_domain);
        }
    });

    async function handleUserSendMessage() {
        const text = elements.chatUserInput.value.trim();
        if (!text) return;

        elements.chatUserInput.value = "";
        appendMessage("user", text);
        scrollToBottom();

        const domain = state.active_chat_domain;
        if (!state.chat_histories[domain]) {
            state.chat_histories[domain] = [];
        }
        state.chat_histories[domain].push({ role: "user", content: text });
        
        const typingId = showTypingIndicator();
        scrollToBottom();

        try {
            const response = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: text,
                    domain: domain,
                    history: state.chat_histories[domain].slice(0, -1)
                })
            });

            removeTypingIndicator(typingId);

            if (response.ok) {
                const data = await response.json();
                if (data.response) {
                    appendMessage("assistant", data.response);
                    state.chat_histories[domain].push({ role: "assistant", content: data.response });
                    await saveUserProfile();
                } else if (data.hata) {
                    appendMessage("assistant", "Hata: " + data.hata);
                }
            } else {
                appendMessage("assistant", "Maalesef sunucu yanıt veremedi. Lütfen tekrar deneyin.");
            }
        } catch (error) {
            removeTypingIndicator(typingId);
            appendMessage("assistant", "Bağlantı hatası oluştu.");
            console.error(error);
        } finally {
            scrollToBottom();
        }
    }

    function showTypingIndicator() {
        const bubble = document.createElement("div");
        bubble.className = "message assistant typing-indicator-bubble";
        bubble.id = "typing-" + Date.now();
        bubble.innerHTML = `
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        elements.chatMessagesArea.appendChild(bubble);
        return bubble.id;
    }

    function removeTypingIndicator(id) {
        const bubble = document.getElementById(id);
        if (bubble) bubble.remove();
    }

    function appendMessage(role, text) {
        const bubble = document.createElement("div");
        bubble.className = `message ${role}`;
        bubble.innerHTML = text.replace(/\n/g, "<br>");
        elements.chatMessagesArea.appendChild(bubble);
    }

    function scrollToBottom() {
        elements.chatMessagesArea.scrollTop = elements.chatMessagesArea.scrollHeight;
    }


    // --- ADVANCED SCHEDULER SECTION ---

    // Load Weekly Schedule
    async function loadWeeklySchedule(step, silent = false, week = 1) {
        if (!state.schedules[step]) {
            state.schedules[step] = {};
        }

        if (state.schedules[step][week]) {
            renderWeeklySchedule(step, week);
            return;
        }

        if (!silent) showLoading(`${week}. Hafta siber çalışma programı çıkarılıyor...`);
        try {
            const response = await fetch("/api/schedule-tasks", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    step_name: step, 
                    career_goal: state.career_goal,
                    week_number: week
                })
            });

            if (response.ok) {
                const data = await response.json();
                state.schedules[step][week] = data;
                await saveUserProfile();
                renderWeeklySchedule(step, week);
            } else {
                if (!silent) alert("Ders planı alınamadı.");
            }
        } catch (error) {
            console.error(error);
            if (!silent) alert("Sunucu bağlantısı koptu.");
        } finally {
            if (!silent) hideLoading();
        }
    }

    // Toggle Manual Edit Mode
    elements.btnToggleEditMode.onclick = () => {
        state.edit_mode = !state.edit_mode;
        
        if (state.edit_mode) {
            elements.btnToggleEditMode.classList.add("active-edit");
            elements.btnToggleEditMode.innerHTML = `<i class="fa-solid fa-check"></i> Düzenlemeyi Kaydet`;
        } else {
            elements.btnToggleEditMode.classList.remove("active-edit");
            elements.btnToggleEditMode.innerHTML = `<i class="fa-solid fa-pen-to-square"></i> Kendim Düzenlemek İstiyorum`;
            saveUserProfile();
        }
        
        renderWeeklySchedule(state.active_step_for_scheduler, state.active_week);
    };

    // Plan Next Week Button
    elements.btnPlanNextWeek.onclick = async () => {
        const step = state.active_step_for_scheduler;
        if (!step) return;

        const currentWeeks = Object.keys(state.schedules[step] || {});
        const nextWeek = currentWeeks.length > 0 ? Math.max(...currentWeeks.map(Number)) + 1 : 1;
        
        state.active_week = nextWeek;
        await loadWeeklySchedule(step, false, nextWeek);
    };

    // Render Weekly Schedule Grid
    function renderWeeklySchedule(step, week = 1) {
        const stepSchedules = state.schedules[step] || {};
        const schedule = stepSchedules[week];

        if (!schedule || !schedule.HaftalikPlan || schedule.HaftalikPlan.length === 0) {
            elements.schedulerEmpty.style.display = "flex";
            elements.schedulerContent.style.display = "none";
            elements.schedulerStepTitle.textContent = "Lütfen Yol Haritası sayfasından planlamak istediğiniz siber güvenlik adımını seçin.";
            return;
        }

        elements.schedulerEmpty.style.display = "none";
        elements.schedulerContent.style.display = "block";
        elements.schedulerStepTitle.innerHTML = `<strong>${step}</strong> adımı için aktif planınız.`;

        // Render Week tabs
        elements.schedulerWeekTabs.innerHTML = "";
        const allWeeks = Object.keys(stepSchedules).map(Number).sort((a,b)=>a-b);
        
        allWeeks.forEach(wNum => {
            const tabBtn = document.createElement("button");
            tabBtn.className = `week-tab-btn ${wNum === week ? 'active' : ''}`;
            tabBtn.textContent = `${wNum}. Hafta`;
            tabBtn.onclick = () => {
                state.active_week = wNum;
                renderWeeklySchedule(step, wNum);
            };
            elements.schedulerWeekTabs.appendChild(tabBtn);
        });

        // Render Days Grid
        elements.weeklyPlannerGrid.innerHTML = "";
        
        schedule.HaftalikPlan.forEach((dayPlan, dayIndex) => {
            const dayRow = document.createElement("div");
            dayRow.className = "planner-day-row";

            const dayTasksContainer = document.createElement("div");
            dayTasksContainer.className = "day-tasks";

            dayPlan.Gorevler.forEach((task, taskIndex) => {
                const taskItem = document.createElement("div");
                taskItem.className = "day-task-item";

                const isAlarmActive = state.reminders.some(r => 
                    r.step === step && 
                    Number(r.week) === Number(week) && 
                    r.day === dayPlan.Gun && 
                    Number(r.taskIndex) === Number(taskIndex) && 
                    r.status === "pending"
                );

                if (state.edit_mode) {
                    taskItem.innerHTML = `
                        <input type="text" class="edit-task-input" value="${task}">
                        <div class="task-actions-wrapper">
                            <button class="btn-task-action alarm ${isAlarmActive ? 'alarm-active' : ''}" title="Alarm Ayarla"><i class="fa-solid fa-clock"></i></button>
                            <button class="btn-task-action delete" title="Görevi Sil"><i class="fa-solid fa-trash-can"></i></button>
                        </div>
                    `;

                    const textInput = taskItem.querySelector(".edit-task-input");
                    textInput.addEventListener("change", () => {
                        dayPlan.Gorevler[taskIndex] = textInput.value.trim();
                    });

                    const btnDelete = taskItem.querySelector(".delete");
                    btnDelete.onclick = () => {
                        dayPlan.Gorevler.splice(taskIndex, 1);
                        renderWeeklySchedule(step, week);
                    };

                } else {
                    taskItem.innerHTML = `
                        <i class="fa-solid fa-chevron-right"></i>
                        <span>${task}</span>
                        <div class="task-actions-wrapper">
                            <button class="btn-task-action alarm ${isAlarmActive ? 'alarm-active' : ''}" title="Alarm Ayarla"><i class="fa-solid fa-clock"></i></button>
                        </div>
                    `;
                }

                const btnAlarm = taskItem.querySelector(".alarm");
                btnAlarm.onclick = () => {
                    activeReminderTask = {
                        step: step,
                        week: week,
                        day: dayPlan.Gun,
                        taskIndex: taskIndex,
                        text: task
                    };

                    elements.reminderTaskText.innerHTML = `<strong>Görev:</strong> ${task}<br><small>${dayPlan.Gun} - ${week}. Hafta</small>`;
                    
                    elements.reminderDatetime.value = "";
                    elements.reminderMessage.value = "";
                    
                    elements.reminderModal.style.display = "flex";
                };

                dayTasksContainer.appendChild(taskItem);
            });

            if (state.edit_mode) {
                const addRow = document.createElement("div");
                addRow.className = "add-task-row";
                addRow.innerHTML = `
                    <input type="text" class="add-task-input" placeholder="Yeni özel görev yazın..." autocomplete="off">
                    <button class="btn-add-task-submit"><i class="fa-solid fa-plus"></i></button>
                `;

                const addInput = addRow.querySelector(".add-task-input");
                const addSubmit = addRow.querySelector(".btn-add-task-submit");

                const submitNewTask = () => {
                    const val = addInput.value.trim();
                    if (val) {
                        dayPlan.Gorevler.push(val);
                        renderWeeklySchedule(step, week);
                    }
                };

                addSubmit.onclick = submitNewTask;
                addInput.onkeydown = (e) => {
                    if (e.key === "Enter") {
                        submitNewTask();
                    }
                };

                dayTasksContainer.appendChild(addRow);
            }

            dayRow.innerHTML = `
                <div class="day-name">${dayPlan.Gun}</div>
                <div class="day-duration">${dayPlan.Sure || '2 Saat'}</div>
            `;
            
            dayRow.insertBefore(dayTasksContainer, dayRow.querySelector(".day-duration"));
            elements.weeklyPlannerGrid.appendChild(dayRow);
        });
    }


    // --- SUGGESTIONS SECTION ---
    async function loadSuggestions(step) {
        showLoading("Siber kaynaklar çekiliyor...");
        try {
            const response = await fetch(`/api/suggestions?topic=${encodeURIComponent(step)}&career_goal=${encodeURIComponent(state.career_goal)}`);
            if (response.ok) {
                const data = await response.json();
                renderSuggestions(step, data);
            } else {
                alert("Öneriler yüklenemedi.");
            }
        } catch (error) {
            console.error(error);
            alert("Bağlantı hatası.");
        } finally {
            hideLoading();
        }
    }

    function renderSuggestions(step, suggestionsList) {
        if (!suggestionsList || suggestionsList.length === 0) {
            elements.suggestionsEmpty.style.display = "flex";
            elements.suggestionsContent.style.display = "none";
            elements.suggestionsStepTitle.textContent = "Yol haritasındaki adımlara yönelik teknik doküman, video ve lablar.";
            return;
        }

        elements.suggestionsEmpty.style.display = "none";
        elements.suggestionsContent.innerHTML = "";
        elements.suggestionsContent.style.display = "grid";
        elements.suggestionsStepTitle.innerHTML = `<strong>${step}</strong> adımı için toplanan en güncel kaynaklar.`;

        suggestionsList.forEach(sugg => {
            const card = document.createElement("div");
            card.className = "suggestion-card animate-message";
            
            let iconClass = "fa-book-open";
            let typeColorClass = "kurs";
            const sType = sugg.type.toLowerCase();
            
            if (sType.includes("video")) {
                iconClass = "fa-circle-play";
                typeColorClass = "video";
            } else if (sType.includes("proje") || sType.includes("lab")) {
                iconClass = "fa-code-branch";
                typeColorClass = "dokümantasyon";
            }
            
            card.innerHTML = `
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                        <span class="sugg-type ${typeColorClass}"><i class="fa-solid ${iconClass}"></i> ${sugg.type}</span>
                    </div>
                    <h4 class="sugg-title" style="margin-bottom:0.5rem; font-size:0.88rem; font-weight:700; line-height:1.3;">${sugg.title}</h4>
                    <p class="sugg-desc" style="font-size:0.75rem; color:var(--text-secondary); line-height:1.4;">${sugg.description}</p>
                </div>
                <a href="${sugg.url}" target="_blank" class="btn-go-source" style="display:inline-flex; align-items:center; gap:0.3rem; color:var(--secondary); text-decoration:none; font-weight:700; font-size:0.75rem; margin-top:0.8rem;">
                    <span>Kaynağa Git</span>
                    <i class="fa-solid fa-arrow-up-right-from-square"></i>
                </a>
            `;
            elements.suggestionsContent.appendChild(card);
        });
    }


    // --- CAREER SIMULATION POD LOGIC ---

    function initSimulationUI() {
        if (!state.career_goal) {
            elements.simulationEmpty.style.display = "flex";
            elements.simulationDashboardArea.style.display = "none";
            elements.simulationRewardBadgeCard.style.display = "none";
        } else {
            elements.simulationEmpty.style.display = "none";
            elements.simulationDashboardArea.style.display = "grid";
            elements.simulationRewardBadgeCard.style.display = "none";

            // Reset Console
            elements.simulationConsoleLogArea.innerHTML = `
                <div class="console-line system-line">> HUD Kapsülü başlatılmaya hazır. Hedef rol yüklendi: ${state.career_goal.toUpperCase()}</div>
                <div class="console-line system-line">> Simülasyonu başlat butonuna basarak 15 saniyelik siber operasyon simülasyonunu başlatın...</div>
            `;

            // Reset Progress circle
            const r = 80;
            const circumference = 2 * Math.PI * r;
            elements.simulationProgressRing.style.strokeDasharray = `${circumference} ${circumference}`;
            elements.simulationProgressRing.style.strokeDashoffset = circumference;
            elements.simulationTimerText.textContent = "15s";
            elements.btnStartSimulation.style.display = "inline-flex";
        }
    }

    elements.btnStartSimulation.onclick = async () => {
        elements.btnStartSimulation.style.display = "none";
        
        elements.simulationConsoleLogArea.innerHTML = `
            <div class="console-line system-line">> Siber kapsül ısıtılıyor...</div>
            <div class="console-line system-line">> Ajanlar verileri OpenAI sunucularından indiriyor...</div>
        `;

        try {
            const response = await fetch("/api/simulation-logs", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ career_goal: state.career_goal })
            });

            if (response.ok) {
                const data = await response.json();
                runSimulationTimer(data.Logs || []);
            } else {
                elements.simulationConsoleLogArea.innerHTML += `
                    <div class="console-line system-line" style="color:var(--accent);">> Sunucu hatası. Yerel simülasyon modu başlatılıyor...</div>
                `;
                runSimulationTimer([
                    "09:00 - Operasyon planlaması yapıldı.",
                    "11:00 - İlk kritik testler gerçekleştirildi.",
                    "13:30 - Sistem performansı optimize edildi.",
                    "15:30 - Ekip içi entegrasyonlar tamamlandı.",
                    "17:00 - Günlük siber çıktılar onaylandı."
                ]);
            }
        } catch (error) {
            console.error("Simulation logs failed to load", error);
            runSimulationTimer([
                "09:00 - Çevrimdışı siber simülasyon başlatıldı.",
                "12:00 - Temel güvenlik analizleri yapıldı.",
                "15:00 - Zafiyet taramaları tamamlandı.",
                "18:00 - Günlük operasyon başarıyla sonlandırıldı."
            ]);
        }
    };

    function runSimulationTimer(logs) {
        elements.simulationConsoleLogArea.innerHTML = `
            <div class="console-line system-line">> BAĞLANTI BAŞARILI. SİBER OPERASYON BAŞLATILDI!</div>
        `;

        const r = 80;
        const circumference = 2 * Math.PI * r;
        
        let startTime = Date.now();
        const duration = 15000; // 15 seconds
        const printedLogIndices = [];

        const simInterval = setInterval(() => {
            const elapsed = Date.now() - startTime;

            if (elapsed >= duration) {
                clearInterval(simInterval);
                finishSimulation();
            } else {
                const remainingSec = Math.ceil((duration - elapsed) / 1000);
                elements.simulationTimerText.textContent = remainingSec + "s";

                // Progress Stroke Dashoffset
                const pct = elapsed / duration;
                const offset = circumference - (pct * circumference);
                elements.simulationProgressRing.style.strokeDashoffset = offset;

                // Log spacing: 15s divided by 5 logs = 3s per log
                const logIndex = Math.floor(elapsed / 3000);
                if (logIndex < logs.length && !printedLogIndices.includes(logIndex)) {
                    printedLogIndices.push(logIndex);
                    
                    const logEl = document.createElement("div");
                    logEl.className = "console-line";
                    elements.simulationConsoleLogArea.appendChild(logEl);
                    
                    // Typewriter effect
                    typeWriter(logEl, `> ${logs[logIndex]}`);
                }
            }
        }, 100);
    }

    function typeWriter(element, text, index = 0) {
        if (index < text.length) {
            element.innerHTML += text.charAt(index);
            elements.simulationConsoleLogArea.scrollTop = elements.simulationConsoleLogArea.scrollHeight;
            setTimeout(() => typeWriter(element, text, index + 1), 20);
        }
    }

    function finishSimulation() {
        elements.simulationTimerText.textContent = "100%";
        elements.simulationProgressRing.style.strokeDashoffset = "0";

        elements.simulationConsoleLogArea.innerHTML += `
            <div class="console-line success-line">> SİBER OPERASYON BAŞARIYLA TAMAMLANDI!</div>
            <div class="console-line system-line">> HUD Kapsülü devreden çıkarılıyor...</div>
        `;
        elements.simulationConsoleLogArea.scrollTop = elements.simulationConsoleLogArea.scrollHeight;

        setTimeout(() => {
            elements.simulationDashboardArea.style.display = "none";
            elements.simulationRewardBadgeCard.style.display = "flex";

            elements.simulationRewardTitle.textContent = `Geleceğin ${state.career_goal} Uzmanı!`;
            elements.simulationRewardDesc.innerHTML = `
                Seçtiğiniz <strong>${state.career_goal}</strong> rolünü 15 saniye boyunca siber konsolda başarıyla simüle ettiniz.<br>
                Zafiyetler kapatıldı, ağ güvenli! Bugün hedefine ulaşmak için ilk adımını atmaya ne dersin?
            `;
        }, 1500);
    }

    // Go to roadmap from simulation badge card
    elements.btnSimulationGoRoadmap.onclick = () => {
        switchPage("#roadmap");
    };

    // Loader Utilities
    function showLoading(text) {
        elements.loadingText.textContent = text;
        elements.loadingSpinner.classList.add("active");
    }

    function hideLoading() {
        elements.loadingSpinner.classList.remove("active");
    }
});
