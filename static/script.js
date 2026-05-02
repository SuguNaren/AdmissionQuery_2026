const chatState = {
    mode: "main",
    selectedCourse: "",
    selectedCourseLabel: "",
    pendingTopic: "",
};

const chatConfig = window.SMC_CHAT_CONFIG || {};

function uniqueItems(items) {
    return [...new Set(items.filter(Boolean))];
}

function endpointCandidates(configuredEndpoint, routePath) {
    const candidates = [];

    if (Array.isArray(configuredEndpoint)) {
        candidates.push(...configuredEndpoint);
    } else if (configuredEndpoint) {
        candidates.push(configuredEndpoint);
    }

    if (window.location.protocol === "http:" || window.location.protocol === "https:") {
        candidates.push(`${window.location.origin}${routePath}`);
    }

    candidates.push(`http://127.0.0.1:8086${routePath}`);
    candidates.push(`http://localhost:8086${routePath}`);

    return uniqueItems(candidates);
}

const chatEndpoints = endpointCandidates(chatConfig.chatEndpoint, "/chat");
const resetEndpoints = endpointCandidates(chatConfig.resetEndpoint, "/reset-chat");
const resolveCourseEndpoints = endpointCandidates(chatConfig.resolveCourseEndpoint, "/resolve-course");

const topicQueries = {
    eligibility: (course) => `eligibility and 12th standard subjects needed to apply for ${course}`,
    subjects: (course) => `what subjects in 12th standard is needed to apply for ${course}`,
    fees: (course) => `fee structure for ${course}`,
    duration: (course) => `duration and semesters for ${course}`,
    details: (course) => `course details for ${course}`,
    admission: (course) => `admission process for ${course}`,
};

function formatCourseName(course) {
    const compact = course.replace(/[^a-z0-9]/gi, "").toLowerCase();
    const names = {
        ba: "B.A.",
        bsc: "B.Sc.",
        bcom: "B.Com.",
        bba: "B.B.A.",
        bca: "B.C.A.",
        bsw: "B.S.W.",
        bva: "B.V.A.",
        ma: "M.A.",
        msc: "M.Sc.",
        mcom: "M.Com.",
        msw: "M.S.W.",
    };

    return names[compact] || course;
}

function setChatVisibility(isOpen) {
    const chatbot = document.getElementById("chatbot");
    const launcher = document.getElementById("chatLauncher");

    if (!chatbot) {
        return;
    }

    chatbot.classList.toggle("chat-hidden", !isOpen);

    if (launcher) {
        launcher.setAttribute("aria-expanded", isOpen ? "true" : "false");
    }

    if (isOpen) {
        const input = document.getElementById("userInput");
        if (input) {
            window.setTimeout(() => input.focus(), 0);
        }
    }
}

function toggleChat() {
    const chatbot = document.getElementById("chatbot");

    if (!chatbot) {
        return;
    }

    setChatVisibility(chatbot.classList.contains("chat-hidden"));
}

function chatbox() {
    return document.getElementById("chatbox");
}

function scrollToBottom() {
    chatbox().scrollTop = chatbox().scrollHeight;
}

function removeQuickReplies() {
    document.querySelectorAll(".quick-replies").forEach((item) => item.remove());
}

function removeLatestPendingMessage() {
    const botMessages = document.querySelectorAll(".bot");
    const lastMessage = botMessages[botMessages.length - 1];

    if (lastMessage && lastMessage.textContent === "Let me check that for you...") {
        lastMessage.remove();
    }
}

function appendMessage(text, type) {
    const message = document.createElement("div");
    message.className = type;
    message.textContent = text;
    chatbox().appendChild(message);
    scrollToBottom();
}

function appendQuickReplies(options) {
    removeQuickReplies();

    const wrapper = document.createElement("div");
    wrapper.className = "quick-replies";

    options.forEach((option) => {
        const button = document.createElement("button");
        button.className = "quick-reply";
        button.type = "button";
        button.textContent = option.label;
        button.addEventListener("click", () => {
            removeQuickReplies();
            appendMessage(option.label, "user");
            option.handler();
        });
        wrapper.appendChild(button);
    });

    chatbox().appendChild(wrapper);
    scrollToBottom();
}

function showMainMenu(isInitial = false) {
    chatState.mode = "main";
    chatState.selectedCourse = "";
    chatState.selectedCourseLabel = "";
    chatState.pendingTopic = "";
    appendMessage(
        isInitial
            ? "Welcome to Stella Maris College (Autonomous). How may I assist you today?"
            : "How may I assist you today?",
        "bot"
    );
    appendQuickReplies([
        {label: "Admission process", handler: () => askBackend("admission process")},
        {label: "Courses", handler: askCourseName},
        {label: "Fee structure", handler: () => askCourseName("fees")},
        {label: "Hostel", handler: () => askBackend("hostel details and facilities")},
        {label: "Ask my own question", handler: askFreeQuestion},
    ]);
}

function askCourseName(topic = "") {
    chatState.mode = "awaitingCourse";
    chatState.pendingTopic = topic;
    chatState.selectedCourse = "";
    chatState.selectedCourseLabel = "";
    appendMessage("Which course are you interested in? Type a course name like BCA, B.Sc Mathematics, B.Com, BBA, BSW, B.V.A., M.A., M.Sc, M.Com, or MSW.", "bot");
}

function askFreeQuestion() {
    chatState.mode = "free";
    appendMessage("Sure. Type your question and I will help you with it.", "bot");
}

function showCourseMenu(courseLabel = chatState.selectedCourseLabel || chatState.selectedCourse) {
    chatState.mode = "courseMenu";

    appendMessage(`What would you like to know about ${courseLabel || "this course"}?`, "bot");
    appendQuickReplies([
        {label: "Eligibility", handler: () => askCourseTopic("eligibility")},
        {label: "12th subjects", handler: () => askCourseTopic("subjects")},
        {label: "Fee structure", handler: () => askCourseTopic("fees")},
        {label: "Duration", handler: () => askCourseTopic("duration")},
        {label: "Course details", handler: () => askCourseTopic("details")},
        {label: "Admission process", handler: () => askCourseTopic("admission")},
        {label: "Choose another course", handler: askCourseName},
        {label: "Main menu", handler: showMainMenu},
    ]);
}

function askCourseTopic(topic) {
    const course = chatState.selectedCourse;
    const buildQuery = topicQueries[topic];

    if (!course || !buildQuery) {
        askCourseName(topic);
        return;
    }

    askBackend(buildQuery(course), () => {
        showCourseMenu(chatState.selectedCourseLabel || course);
    });
}

function finalizeCourseSelection(course) {
    chatState.selectedCourse = course.selection_query;
    chatState.selectedCourseLabel = course.label;

    if (chatState.pendingTopic) {
        const topic = chatState.pendingTopic;
        chatState.pendingTopic = "";
        chatState.mode = "courseMenu";
        askCourseTopic(topic);
        return;
    }

    showCourseMenu(course.label);
}

function resolveCourseChoice(query) {
    appendMessage("Let me check that for you...", "bot");

    postJsonWithFallback(resolveCourseEndpoints, {query})
        .then((res) => res.json())
        .then((data) => {
            removeLatestPendingMessage();

            if (data.status === "selected" && data.course) {
                finalizeCourseSelection(data.course);
                return;
            }

            if (data.status === "variant_required" && Array.isArray(data.options) && data.options.length > 0) {
                chatState.mode = "awaitingCourse";
                const hasFundingChoice = data.options.some((option) => (option.variant_label || "").toLowerCase().includes("aided"))
                    && data.options.some((option) => (option.variant_label || "").toLowerCase().includes("self-financing"));
                appendMessage(
                    hasFundingChoice
                        ? `I found both aided and self-financing options for ${data.course_name}. Please choose one.`
                        : `I found multiple options for ${data.course_name}. Please choose one.`,
                    "bot"
                );
                appendQuickReplies(
                    data.options.map((option) => ({
                        label: option.variant_label || option.label,
                        handler: () => finalizeCourseSelection(option),
                    }))
                );
                return;
            }

            if (data.status === "course_required" && Array.isArray(data.options) && data.options.length > 0) {
                chatState.mode = "awaitingCourse";
                appendMessage("I found multiple course matches. Please choose the one you mean.", "bot");
                appendQuickReplies(
                    data.options.map((option) => ({
                        label: option.label,
                        handler: () => resolveCourseChoice(option.selection_query),
                    }))
                );
                return;
            }

            appendMessage(data.message || "I couldn’t match that course in the prospectus yet. Please type the full course name.", "bot");
        })
        .catch((error) => {
            removeLatestPendingMessage();
            console.warn("Course resolution failed for all candidate endpoints.", resolveCourseEndpoints, error);
            appendMessage("I could not verify that course right now. Please try again.", "bot");
        });
}

function handleCourseInput(course) {
    resolveCourseChoice(course);
}

function askBackend(message, afterReply) {
    appendMessage("Let me check that for you...", "bot");

    postJsonWithFallback(chatEndpoints, {message})
        .then((res) => res.json())
        .then((data) => {
            removeLatestPendingMessage();

            appendMessage(data.reply, "bot");

            if (afterReply) {
                afterReply();
            } else {
                appendQuickReplies([
                    {label: "Main menu", handler: showMainMenu},
                    {label: "Ask another question", handler: askFreeQuestion},
                ]);
            }
        })
        .catch((error) => {
            removeLatestPendingMessage();
            console.warn("Chat request failed for all candidate endpoints.", chatEndpoints, error);
            appendMessage("I could not reach the server. Please try again.", "bot");
        });
}

function postJsonWithFallback(urls, payload) {
    let lastError = null;

    return urls.reduce((chain, url) => {
        return chain.catch(() => {
            return fetch(url, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(payload),
            }).then((response) => {
                if (!response.ok) {
                    throw new Error(`Request to ${url} failed with status ${response.status}`);
                }

                return response;
            });
        });
    }, Promise.reject(new Error("No request attempted"))).catch((error) => {
        lastError = error;
        throw lastError;
    });
}

function sendMessage() {
    const inputField = document.getElementById("userInput");
    const input = inputField.value.trim();

    if (input === "") return;

    removeQuickReplies();
    appendMessage(input, "user");
    inputField.value = "";

    if (chatState.mode === "awaitingCourse") {
        handleCourseInput(input);
        return;
    }

    askBackend(input);
}

document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("userInput");
    if (!input) {
        return;
    }

    if (document.getElementById("chatLauncher")) {
        setChatVisibility(false);
    }

    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    postJsonWithFallback(resetEndpoints, {})
        .catch((error) => {
            console.warn("Reset request failed for all candidate endpoints.", resetEndpoints, error);
            return null;
        })
        .finally(() => {
            showMainMenu(true);
        });
});
