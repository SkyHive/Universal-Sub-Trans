<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAppStore } from './store/app';
import { bridge } from './api/bridge';
import {
    FileVideo,
    Settings as SettingsIcon,
    Play,
    CheckCircle,
    Loader2,
    ChevronRight,
    Database,
    Cpu,
    Globe,
    Minus,
    X,
    Monitor,
    AlertTriangle,
    Download,
    RefreshCw
} from 'lucide-vue-next';
import { translations, type Language } from './i18n';
import { computed } from 'vue';

const store = useAppStore();
const activeTab = ref('translate');
const selectedFilePath = ref<string | null>(null);
const currentLang = computed(() => (store.config?.app.language as Language) || 'en');
const t = computed(() => translations[currentLang.value]);

// Settings feedback state
const saveStatus = ref<'idle' | 'saving' | 'success' | 'error'>('idle');
const saveMessage = ref('');

onMounted(async () => {
    await store.fetchConfig();
    await store.checkSystemStatus();

    // Setup global event listener for backend events
    window.onBackendEvent = (event: string, data: any) => {
        switch (event) {
            case 'status_update':
                store.updateStatus(data);
                break;
            case 'task_completed':
                store.completeTask(data);
                break;
            case 'task_failed':
                store.taskFailed(data);
                break;
            case 'dep_install_progress':
                store.updateInstallProgress(data.progress);
                break;
            case 'dep_install_completed':
                store.completeInstallation(t.value.installSuccess);
                break;
            case 'dep_install_failed':
                store.installationFailed(t.value.installError);
                break;
        }
    };
});

const handleSelectFile = async () => {
    const path = await bridge.selectFile();
    if (path) {
        selectedFilePath.value = path;
    }
};


const saveSettings = async () => {
    if (store.config) {
        saveStatus.value = 'saving';
        try {
            await store.saveConfig(store.config);
            saveStatus.value = 'success';
            saveMessage.value = t.value.settingsSaved;
        } catch (err) {
            saveStatus.value = 'error';
            saveMessage.value = t.value.settingsError;
        }
        setTimeout(() => {
            saveStatus.value = 'idle';
        }, 3000);
    }
};

const handleInstallDeps = async () => {
    await store.installDependencies();
};

const handleMinimize = () => bridge.minimize();
const handleClose = () => bridge.close();

// Resume Logic
const showResumeModal = ref(false);
const resumePoints = ref<{ has_audio: boolean, has_transcript: boolean } | null>(null);

const handleStart = async () => {
    if (!selectedFilePath.value) return;

    // Check if we can resume
    const points = await store.checkResumePoint(selectedFilePath.value);
    if (points.has_audio || points.has_transcript) {
        resumePoints.value = points;
        showResumeModal.value = true;
    } else {
        await store.startTask(selectedFilePath.value, currentLang.value === 'zh' ? 'Chinese' : 'English', "fresh");
    }
};

const handleResumeDecision = async (mode: string) => {
    showResumeModal.value = false;
    if (selectedFilePath.value) {
        await store.startTask(selectedFilePath.value, currentLang.value === 'zh' ? 'Chinese' : 'English', mode);
    }
};

// Manual Drag Implementation
const isDragging = ref(false);
const dragStartPos = ref({ x: 0, y: 0 });
const windowStartPos = ref({ x: 0, y: 0 });

const onDragStart = async (e: MouseEvent) => {
    // Only start drag if clicking on the drag region
    if ((e.target as HTMLElement).classList.contains('drag-region')) {
        isDragging.value = true;
        dragStartPos.value = { x: e.screenX, y: e.screenY };
        windowStartPos.value = await bridge.getPosition();

        window.addEventListener('mousemove', onDragging);
        window.addEventListener('mouseup', onDragEnd);
    }
};

const onDragging = (e: MouseEvent) => {
    if (isDragging.value) {
        const dx = e.screenX - dragStartPos.value.x;
        const dy = e.screenY - dragStartPos.value.y;
        bridge.moveWindow(windowStartPos.value.x + dx, windowStartPos.value.y + dy);
    }
};

const onDragEnd = () => {
    isDragging.value = false;
    window.removeEventListener('mousemove', onDragging);
    window.removeEventListener('mouseup', onDragEnd);
};

const isCheckingDeps = ref(false);
const handleManualCheck = async () => {
    isCheckingDeps.value = true;
    try {
        await store.checkSystemStatus();
    } finally {
        isCheckingDeps.value = false;
    }
};
</script>

<template>
    <div class="flex h-screen bg-background text-foreground transition-colors duration-300 dark overflow-hidden selection:bg-primary/30"
        @mousedown="onDragStart">

        <!-- Custom Title Bar (Only for Frameless) -->
        <div class="fixed top-0 left-0 right-0 h-10 z-[100] flex items-center justify-between pointer-events-none">
            <div class="flex-1 h-full drag-region pointer-events-auto"></div>
            <div class="flex items-center h-full pointer-events-auto px-2 space-x-1">
                <button @click="handleMinimize"
                    class="w-10 h-10 flex items-center justify-center hover:bg-white/10 transition-colors rounded-lg group">
                    <Minus class="w-4 h-4 text-muted-foreground group-hover:text-foreground" />
                </button>
                <button @click="handleClose"
                    class="w-10 h-10 flex items-center justify-center hover:bg-red-500/80 transition-colors rounded-lg group">
                    <X class="w-4 h-4 text-muted-foreground group-hover:text-white" />
                </button>
            </div>
        </div>

        <!-- Sidebar -->
        <aside
            class="w-64 border-r border-border bg-card/50 backdrop-blur-3xl flex flex-col p-6 pt-10 space-y-8 relative">
            <div class="flex items-center space-x-3 mb-4">
                <div
                    class="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-primary-foreground shadow-lg shadow-primary/20">
                    <Globe class="w-6 h-6" />
                </div>
                <h1 class="text-xl font-bold tracking-tight">UniSub</h1>
            </div>

            <nav class="flex-1 space-y-1">
                <button @click="activeTab = 'translate'" :class="[
                    'w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 group',
                    activeTab === 'translate' ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/10' : 'hover:bg-accent/50 text-muted-foreground hover:text-foreground'
                ]">
                    <FileVideo class="w-5 h-5 transition-transform group-hover:scale-110" />
                    <span class="font-medium">{{ t.translate }}</span>
                </button>
                <button @click="activeTab = 'settings'" :class="[
                    'w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 group',
                    activeTab === 'settings' ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/10' : 'hover:bg-accent/50 text-muted-foreground hover:text-foreground'
                ]">
                    <SettingsIcon class="w-5 h-5 transition-transform group-hover:rotate-45" />
                    <span class="font-medium">{{ t.settings }}</span>
                </button>
                <button @click="activeTab = 'system'" :class="[
                    'w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 group',
                    activeTab === 'system' ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/10' : 'hover:bg-accent/50 text-muted-foreground hover:text-foreground'
                ]">
                    <Monitor class="w-5 h-5 transition-transform group-hover:scale-110" />
                    <span class="font-medium">{{ t.system }}</span>
                </button>
            </nav>

            <div
                class="p-4 rounded-2xl bg-gradient-to-br from-accent/40 to-accent/10 border border-white/5 text-[10px] space-y-2">
                <div class="flex items-center justify-between opacity-50">
                    <span class="font-mono uppercase">STT Engine</span>
                    <Cpu class="w-3 h-3" />
                </div>
                <p class="font-semibold text-xs">{{ store.config?.whisper.model_size }}</p>

                <div class="flex items-center justify-between opacity-50 mt-4">
                    <span class="font-mono uppercase">Translator</span>
                    <Database class="w-3 h-3" />
                </div>
                <p class="font-semibold text-xs truncate">{{ store.config?.ai.model_name }}</p>
            </div>
        </aside>

        <!-- Main Content -->
        <main
            class="flex-1 flex flex-col overflow-hidden bg-gradient-to-br from-background via-background to-primary/5 pt-10">

            <!-- Translate Tab -->
            <div v-if="activeTab === 'translate'"
                class="flex-1 flex flex-col p-10 space-y-10 overflow-y-auto custom-scrollbar">
                <header class="animate-in fade-in slide-in-from-top duration-700">
                    <h2 class="text-4xl font-extrabold tracking-tight">{{ t.generateSubtitles }}</h2>
                    <p class="text-muted-foreground mt-2 text-lg">{{ t.aiPowered }}</p>
                </header>

                <!-- Dropzone -->
                <div @click="handleSelectFile"
                    class="relative group cursor-pointer border-2 border-dashed border-border/50 hover:border-primary/50 rounded-[40px] p-16 flex flex-col items-center justify-center transition-all duration-500 bg-card/20 hover:bg-card/40 backdrop-blur-sm overflow-hidden animate-in zoom-in duration-500">
                    <div
                        class="absolute inset-0 bg-gradient-to-tr from-primary/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700">
                    </div>

                    <div v-if="!selectedFilePath" class="relative z-10 flex flex-col items-center">
                        <div
                            class="w-20 h-20 bg-accent rounded-[30px] flex items-center justify-center mb-8 text-primary shadow-2xl group-hover:rotate-6 transition-transform duration-500">
                            <FileVideo class="w-10 h-10" />
                        </div>
                        <p class="text-2xl font-bold tracking-tight">{{ t.dropVideo }}</p>
                        <p class="text-muted-foreground mt-3 font-medium">{{ t.orBrowse }}</p>
                    </div>

                    <div v-else class="relative z-10 flex flex-col items-center w-full px-8 text-center">
                        <div
                            class="w-20 h-20 bg-primary/10 text-primary rounded-[30px] flex items-center justify-center mb-8 animate-bounce-subtle">
                            <CheckCircle class="w-10 h-10" />
                        </div>
                        <p class="text-2xl font-bold italic truncate max-w-lg mb-2">{{
                            selectedFilePath.split('\\').pop()?.split('/').pop() }}</p>
                        <button @click.stop="selectedFilePath = null"
                            class="text-sm font-bold text-primary hover:text-primary/80 transition-colors uppercase tracking-widest mt-4">{{
                                t.changeVideo }}</button>
                    </div>
                </div>

                <!-- Action -->
                <div v-if="selectedFilePath" class="space-y-8 animate-in slide-in-from-bottom duration-500">
                    <div class="flex items-center justify-between gap-10">
                        <button @click="handleStart" :disabled="store.isProcessing"
                            class="flex-1 py-5 bg-primary text-primary-foreground rounded-[25px] font-black text-xl flex items-center justify-center space-x-4 shadow-2xl shadow-primary/30 hover:shadow-primary/50 hover:-translate-y-1 active:translate-y-0 disabled:opacity-50 disabled:translate-y-0 transition-all duration-300 min-w-fit">
                            <Loader2 v-if="store.isProcessing" class="w-7 h-7 animate-spin" />
                            <Play v-else class="w-7 h-7 fill-current" />
                            <span class="whitespace-nowrap">{{ store.isProcessing ? t.processingAudio :
                                t.startProduction }}</span>
                        </button>
                        <div class="shrink-0 text-right max-w-[200px]">
                            <p class="text-xs font-bold opacity-50 mb-1 leading-tight">{{
                                store.statusMessage || t.systemReady }}</p>
                            <p v-if="store.isProcessing"
                                class="text-5xl font-black tabular-nums tracking-tighter text-primary">{{
                                    store.currentProgress }}%</p>
                        </div>
                    </div>

                    <div v-if="store.isProcessing"
                        class="w-full h-4 bg-accent/30 rounded-full overflow-hidden p-1 border border-white/5">
                        <div class="h-full bg-gradient-to-r from-primary to-primary/60 rounded-full transition-all duration-700 ease-out relative"
                            :style="{ width: `${store.currentProgress}%` }">
                            <div
                                class="absolute inset-0 bg-[linear-gradient(90deg,transparent_0%,rgba(255,255,255,0.3)_50%,transparent_100%)] animate-shimmer">
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Results -->
                <div v-if="store.results.length > 0" class="space-y-6 pt-6 animate-in fade-in duration-1000">
                    <h3 class="text-2xl font-black flex items-center tracking-tight">
                        <CheckCircle class="w-7 h-7 text-green-500 mr-3" />
                        {{ t.transcriptionOutput }}
                    </h3>
                    <div class="grid grid-cols-1 gap-6">
                        <div v-for="(seg, idx) in store.results.slice(0, 15)" :key="idx"
                            class="p-6 rounded-[30px] bg-card/40 border border-white/5 shadow-xl flex flex-col md:flex-row md:items-start gap-4 group hover:bg-card/60 hover:border-primary/20 transition-all duration-300">
                            <div
                                class="font-mono text-[10px] tracking-tighter bg-accent/50 text-accent-foreground px-3 py-1 rounded-full w-fit shrink-0 opacity-60">
                                {{ seg.start.toFixed(2) }}s → {{ seg.end.toFixed(2) }}s
                            </div>
                            <div class="flex-1 space-y-2">
                                <p class="text-sm text-muted-foreground italic leading-relaxed">{{ seg.text }}</p>
                                <p class="text-xl font-bold tracking-tight leading-snug">{{ seg.translated_text }}</p>
                            </div>
                        </div>
                    </div>
                    <p v-if="store.results.length > 15"
                        class="text-center text-sm font-bold opacity-30 py-10 uppercase tracking-[0.2em]">
                        + {{ store.results.length - 15 }} {{ t.moreSegments }}
                    </p>
                </div>
            </div>

            <!-- Settings Tab -->
            <div v-if="activeTab === 'settings'"
                class="flex-1 p-10 space-y-12 overflow-y-auto custom-scrollbar animate-in slide-in-from-right duration-500">
                <header>
                    <h2 class="text-4xl font-extrabold tracking-tight">{{ t.preferences }}</h2>
                    <p class="text-muted-foreground mt-2 text-lg">{{ t.tuneEngines }}</p>
                </header>

                <div v-if="store.config" class="max-w-3xl space-y-12 pb-32">

                    <section class="space-y-6 bg-card/20 p-8 rounded-[35px] border border-white/5 backdrop-blur-md">
                        <h3 class="text-xs font-black uppercase tracking-[0.2em] text-primary flex items-center">
                            <Database class="w-4 h-4 mr-3" />
                            {{ t.llm }}
                        </h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="md:col-span-2 space-y-2">
                                <label class="text-xs font-bold uppercase opacity-50 ml-1">{{ t.apiBase }}</label>
                                <input v-model="store.config.ai.base_url"
                                    class="w-full px-5 py-4 rounded-2xl bg-background/50 border border-border focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all font-medium" />
                            </div>
                            <div class="md:col-span-2 space-y-2">
                                <label class="text-xs font-bold uppercase opacity-50 ml-1">{{ t.apiKey }}</label>
                                <input v-model="store.config.ai.api_key" type="password"
                                    class="w-full px-5 py-4 rounded-2xl bg-background/50 border border-border focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all font-medium" />
                            </div>
                            <div class="space-y-2">
                                <label class="text-xs font-bold uppercase opacity-50 ml-1">{{ t.activeModel }}</label>
                                <input v-model="store.config.ai.model_name"
                                    class="w-full px-5 py-4 rounded-2xl bg-background/50 border border-border focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all font-medium" />
                            </div>
                            <div class="space-y-2">
                                <label class="text-xs font-bold uppercase opacity-50 ml-1">{{ t.batchSize }}</label>
                                <input v-model.number="store.config.ai.batch_size" type="number"
                                    class="w-full px-5 py-4 rounded-2xl bg-background/50 border border-border focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all font-medium" />
                            </div>
                            <div class="md:col-span-2 space-y-2">
                                <label class="text-xs font-bold uppercase opacity-50 ml-1">{{ t.customBatchPrompt
                                }}</label>
                                <textarea v-model="store.config.ai.system_prompt" rows="6"
                                    class="w-full px-5 py-4 rounded-2xl bg-background/50 border border-border focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all font-medium text-xs font-mono custom-scrollbar resize-none"></textarea>
                            </div>
                            <div class="md:col-span-2 space-y-2">
                                <label class="text-xs font-bold uppercase opacity-50 ml-1">{{ t.fallbackPrompt
                                }}</label>
                                <textarea v-model="store.config.ai.fallback_prompt" rows="4"
                                    class="w-full px-5 py-4 rounded-2xl bg-background/50 border border-border focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all font-medium text-xs font-mono custom-scrollbar resize-none"></textarea>
                            </div>
                        </div>
                    </section>

                    <section class="space-y-6 bg-card/20 p-8 rounded-[35px] border border-white/5 backdrop-blur-md">
                        <h3 class="text-xs font-black uppercase tracking-[0.2em] text-primary flex items-center">
                            <Cpu class="w-4 h-4 mr-3" />
                            {{ t.sttNetwork }}
                        </h3>
                        <div class="grid grid-cols-2 gap-6">
                            <div class="space-y-2">
                                <label class="text-xs font-bold uppercase opacity-50 ml-1">{{ t.parameterCount
                                    }}</label>
                                <select v-model="store.config.whisper.model_size"
                                    class="w-full px-5 py-4 rounded-2xl bg-background/50 border border-border focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all font-bold appearance-none">
                                    <option value="tiny">{{ t.tiny }}</option>
                                    <option value="base">{{ t.base }}</option>
                                    <option value="small">{{ t.small }}</option>
                                    <option value="medium">{{ t.medium }}</option>
                                    <option value="large-v3">{{ t.large }}</option>
                                </select>
                            </div>
                            <div class="space-y-2">
                                <label class="text-xs font-bold uppercase opacity-50 ml-1">{{ t.computeCore }}</label>
                                <select v-model="store.config.whisper.device"
                                    class="w-full px-5 py-4 rounded-2xl bg-background/50 border border-border focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all font-bold appearance-none">
                                    <option value="auto">{{ t.autoDetect }}</option>
                                    <option value="cuda">{{ t.cuda }}</option>
                                    <option value="cpu">{{ t.cpu }}</option>
                                </select>
                            </div>
                        </div>
                    </section>
                    <section class="space-y-6 bg-card/20 p-8 rounded-[35px] border border-white/5 backdrop-blur-md">
                        <h3 class="text-xs font-black uppercase tracking-[0.2em] text-primary flex items-center">
                            <Globe class="w-4 h-4 mr-3" />
                            {{ t.generalNetwork }}
                        </h3>
                        <div class="space-y-6">
                            <div class="space-y-2">
                                <label class="text-xs font-bold uppercase opacity-50 ml-1">{{ t.pypiMirror }}</label>
                                <input v-model="store.config.app.pypi_mirror" placeholder="https://pypi.org"
                                    class="w-full px-5 py-4 rounded-2xl bg-background/50 border border-border focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all font-medium" />
                                <p class="text-[10px] opacity-40 ml-1">{{ t.pypiHint }}</p>
                            </div>
                            <div class="space-y-2">
                                <label class="text-xs font-bold uppercase opacity-50 ml-1">{{ t.outputDir }}</label>
                                <input v-model="store.config.app.output_dir"
                                    class="w-full px-5 py-4 rounded-2xl bg-background/50 border border-border focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all font-medium" />
                            </div>
                            <div class="space-y-2">
                                <label class="text-xs font-bold uppercase opacity-50 ml-1">{{ t.uiLanguage }}</label>
                                <select v-model="store.config.app.language"
                                    class="w-full px-5 py-4 rounded-2xl bg-background/50 border border-border focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all font-bold appearance-none">
                                    <option value="en">English</option>
                                    <option value="zh">简体中文</option>
                                </select>
                            </div>
                            <div class="space-y-2">
                                <label class="text-xs font-bold uppercase opacity-50 ml-1">{{ t.logLevel }}</label>
                                <select v-model="store.config.app.log_level"
                                    class="w-full px-5 py-4 rounded-2xl bg-background/50 border border-border focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all font-bold appearance-none">
                                    <option value="DEBUG">DEBUG</option>
                                    <option value="INFO">INFO</option>
                                    <option value="WARNING">WARNING</option>
                                    <option value="ERROR">ERROR</option>
                                </select>
                                <p class="text-[10px] opacity-40 ml-1">{{ t.logHint }}</p>
                            </div>
                        </div>
                    </section>

                    <div class="space-y-4">
                        <button @click="saveSettings" :disabled="saveStatus === 'saving'"
                            class="w-full py-5 bg-foreground text-background rounded-[25px] font-black text-lg shadow-2xl hover:bg-foreground/90 hover:-translate-y-1 active:translate-y-0 transition-all duration-300 disabled:opacity-50 disabled:translate-y-0">
                            <Loader2 v-if="saveStatus === 'saving'" class="w-6 h-6 animate-spin mx-auto" />
                            <span v-else>{{ t.applySettings }}</span>
                        </button>

                        <div v-if="saveStatus !== 'idle' && saveStatus !== 'saving'"
                            :class="['text-center text-sm font-bold p-4 rounded-2xl transition-all duration-500 animate-in fade-in slide-in-from-top-4',
                                saveStatus === 'success' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500']">
                            {{ saveMessage }}
                        </div>
                    </div>
                </div>
            </div>

            <!-- System Tab -->
            <div v-if="activeTab === 'system'"
                class="flex-1 p-10 space-y-12 overflow-y-auto custom-scrollbar animate-in slide-in-from-right duration-500">
                <header class="flex items-start justify-between">
                    <div>
                        <h2 class="text-4xl font-extrabold tracking-tight">{{ t.systemStatus }}</h2>
                        <p class="text-muted-foreground mt-2 text-lg">{{ t.hardwareRuntime }}</p>
                    </div>
                    <button @click="handleManualCheck" :disabled="isCheckingDeps"
                        class="p-4 bg-accent/50 hover:bg-accent text-foreground rounded-2xl transition-all flex items-center space-x-2 group">
                        <RefreshCw
                            :class="['w-5 h-5', isCheckingDeps ? 'animate-spin' : 'group-hover:rotate-180 transition-transform duration-500']" />
                        <span class="font-bold">{{ t.checkAgain }}</span>
                    </button>
                </header>

                <div class="max-w-3xl space-y-8">
                    <!-- Hardware Detection Card -->
                    <section class="bg-card/20 p-8 rounded-[35px] border border-white/5 backdrop-blur-md space-y-6">
                        <div class="flex items-center justify-between">
                            <h3 class="text-xs font-black uppercase tracking-[0.2em] text-primary flex items-center">
                                <Cpu class="w-4 h-4 mr-3" />
                                {{ t.hardwareLogic }}
                            </h3>
                            <span
                                class="px-3 py-1 rounded-full bg-primary/10 text-primary text-[10px] font-bold uppercase tracking-widest">
                                Online
                            </span>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div class="space-y-1">
                                <p class="text-xs font-bold uppercase opacity-30">{{ t.primaryGpu }}</p>
                                <p class="text-2xl font-black capitalize">{{ store.systemStatus.gpu_vendor }}</p>
                            </div>
                            <div class="space-y-1">
                                <p class="text-xs font-bold uppercase opacity-30">{{ t.architecture }}</p>
                                <p class="text-2xl font-black">X86_64</p>
                            </div>
                        </div>
                    </section>

                    <!-- Dependencies Card -->
                    <section class="bg-card/20 p-8 rounded-[35px] border border-white/5 backdrop-blur-md space-y-8">
                        <div class="flex items-center justify-between">
                            <h3 class="text-xs font-black uppercase tracking-[0.2em] text-primary flex items-center">
                                <Database class="w-4 h-4 mr-3" />
                                {{ t.aiDeps }}
                            </h3>
                        </div>

                        <!-- Status: Ready -->
                        <div v-if="store.systemStatus.can_accelerate && !store.systemStatus.needs_install"
                            class="flex items-center space-x-6 p-6 rounded-3xl bg-green-500/10 border border-green-500/20">
                            <div
                                class="w-14 h-14 rounded-2xl bg-green-500/20 flex items-center justify-center text-green-500">
                                <CheckCircle class="w-8 h-8" />
                            </div>
                            <div>
                                <p class="text-xl font-bold text-green-500">{{ t.accelReady }}</p>
                                <p class="text-sm opacity-60">{{ t.cudaInitialized }}</p>
                            </div>
                        </div>

                        <!-- Status: Missing -->
                        <div v-else-if="store.systemStatus.can_accelerate && store.systemStatus.needs_install"
                            class="space-y-6">
                            <div
                                class="flex items-center space-x-6 p-6 rounded-3xl bg-amber-500/10 border border-amber-500/20">
                                <div
                                    class="w-14 h-14 rounded-2xl bg-amber-500/20 flex items-center justify-center text-amber-500">
                                    <AlertTriangle class="w-8 h-8" />
                                </div>
                                <div>
                                    <p class="text-xl font-bold text-amber-500">{{ t.depsMissing }}</p>
                                    <p class="text-sm opacity-60">{{ t.gpuDetectedLibReq }}</p>
                                </div>
                            </div>

                            <div v-if="store.systemStatus.is_installing" class="space-y-4">
                                <div
                                    class="flex items-center justify-between text-sm font-bold uppercase tracking-widest">
                                    <span>{{ t.downloadingCudnn }}</span>
                                    <span class="text-primary">{{ Math.round(store.systemStatus.install_progress)
                                        }}%</span>
                                </div>
                                <div
                                    class="w-full h-3 bg-accent/30 rounded-full overflow-hidden p-1 border border-white/5">
                                    <div class="h-full bg-primary rounded-full transition-all duration-300 relative"
                                        :style="{ width: `${store.systemStatus.install_progress}%` }">
                                        <div class="absolute inset-0 bg-white/20 animate-shimmer"></div>
                                    </div>
                                </div>
                            </div>

                            <button v-else @click="handleInstallDeps"
                                class="w-full py-5 bg-primary text-primary-foreground rounded-2xl font-black text-lg shadow-xl hover:-translate-y-1 active:translate-y-0 transition-all flex items-center justify-center space-x-3">
                                <Download class="w-6 h-6" />
                                <span>{{ t.installGpuSupport }}</span>
                            </button>
                        </div>

                        <!-- Status: Not Applicable (AMD/Intel) -->
                        <div v-else
                            class="flex items-center space-x-6 p-6 rounded-3xl bg-blue-500/10 border border-blue-500/20">
                            <div
                                class="w-14 h-14 rounded-2xl bg-blue-500/20 flex items-center justify-center text-blue-500">
                                <Cpu class="w-8 h-8" />
                            </div>
                            <div>
                                <p class="text-xl font-bold text-blue-500">{{ t.universalCpuMode }}</p>
                                <p class="text-sm opacity-60">{{ t.cpuFallback }}</p>
                            </div>
                        </div>
                    </section>

                    <div class="p-6 rounded-2xl bg-accent/20 border border-white/5">
                        <p class="text-xs leading-relaxed opacity-50">{{ t.gpuNote }}</p>
                    </div>
                </div>
            </div>
        </main>

        <!-- Resume Task Modal -->
        <div v-if="showResumeModal"
            class="fixed inset-0 z-[200] flex items-center justify-center p-6 bg-background/80 backdrop-blur-xl animate-in fade-in duration-300">
            <div
                class="max-w-md w-full bg-card border border-white/10 rounded-[40px] p-8 shadow-2xl space-y-8 animate-in zoom-in duration-500">
                <div class="flex flex-col items-center text-center space-y-4">
                    <div class="w-20 h-20 bg-primary/20 text-primary rounded-[30px] flex items-center justify-center">
                        <Database class="w-10 h-10" />
                    </div>
                    <h3 class="text-2xl font-black">{{ t.restoreProgress }}</h3>
                    <p class="text-muted-foreground">{{ t.restoreDesc }}</p>
                </div>

                <div class="grid grid-cols-1 gap-4">
                    <button v-if="resumePoints?.has_transcript" @click="handleResumeDecision('use_transcript')"
                        class="w-full p-6 rounded-3xl bg-primary text-primary-foreground hover:scale-[1.02] active:scale-100 transition-all text-left flex items-center space-x-4">
                        <CheckCircle class="w-8 h-8 opacity-60" />
                        <div>
                            <p class="font-bold">{{ t.resumeTrans }}</p>
                            <p class="text-xs opacity-70">{{ t.skipStt }}</p>
                        </div>
                    </button>

                    <button v-if="resumePoints?.has_audio" @click="handleResumeDecision('use_audio')"
                        class="w-full p-6 rounded-3xl bg-accent text-foreground hover:scale-[1.02] active:scale-100 transition-all text-left flex items-center space-x-4">
                        <Play class="w-8 h-8 opacity-60" />
                        <div>
                            <p class="font-bold">{{ t.useExistingAudio }}</p>
                            <p class="text-xs opacity-70">{{ t.rerunStt }}</p>
                        </div>
                    </button>

                    <button @click="handleResumeDecision('fresh')"
                        class="w-full p-6 rounded-3xl border border-white/5 hover:bg-white/5 transition-all text-left flex items-center space-x-4">
                        <Loader2 class="w-8 h-8 opacity-40" />
                        <div>
                            <p class="font-bold opacity-60">{{ t.startFresh }}</p>
                            <p class="text-xs opacity-40">{{ t.cleanTemp }}</p>
                        </div>
                    </button>

                    <button @click="showResumeModal = false"
                        class="w-full py-4 text-xs font-bold uppercase tracking-widest opacity-30 hover:opacity-100">{{
                            t.cancel }}</button>
                </div>
            </div>
        </div>
    </div>
</template>

<style>
.drag-region {
    -webkit-app-region: drag;
}

button {
    -webkit-app-region: no-drag;
}

@keyframes shimmer {
    0% {
        transform: translateX(-100%);
    }

    100% {
        transform: translateX(100%);
    }
}

.animate-shimmer {
    animation: shimmer 2s infinite;
}

@keyframes bounce-subtle {

    0%,
    100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-5px);
    }
}

.animate-bounce-subtle {
    animation: bounce-subtle 3s infinite ease-in-out;
}

/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
    width: 5px;
}

.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 9999px;
    transition: background-color 0.3s;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: rgba(var(--primary), 0.5);
}

.selection\:bg-primary\/30 ::selection {
    background-color: hsla(var(--primary), 0.3);
}
</style>
