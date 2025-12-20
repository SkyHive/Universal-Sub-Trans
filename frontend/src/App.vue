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
    X
} from 'lucide-vue-next';

const store = useAppStore();
const activeTab = ref('translate');
const selectedFilePath = ref<string | null>(null);

onMounted(async () => {
    await store.fetchConfig();
});

const handleSelectFile = async () => {
    const path = await bridge.selectFile();
    if (path) {
        selectedFilePath.value = path;
    }
};

const handleStart = async () => {
    if (selectedFilePath.value) {
        await store.startTask(selectedFilePath.value, "Chinese");
    }
};

const saveSettings = async () => {
    if (store.config) {
        await store.saveConfig(store.config);
    }
};

const handleMinimize = () => bridge.minimize();
const handleClose = () => bridge.close();

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
                    <span class="font-medium">Translate</span>
                </button>
                <button @click="activeTab = 'settings'" :class="[
                    'w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 group',
                    activeTab === 'settings' ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/10' : 'hover:bg-accent/50 text-muted-foreground hover:text-foreground'
                ]">
                    <SettingsIcon class="w-5 h-5 transition-transform group-hover:rotate-45" />
                    <span class="font-medium">Settings</span>
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
                    <h2 class="text-4xl font-extrabold tracking-tight">Generate Subtitles</h2>
                    <p class="text-muted-foreground mt-2 text-lg">AI-powered transcription and translation in one click.
                    </p>
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
                        <p class="text-2xl font-bold tracking-tight">Drop your video here</p>
                        <p class="text-muted-foreground mt-3 font-medium">Or click to browse your files</p>
                    </div>

                    <div v-else class="relative z-10 flex flex-col items-center w-full px-8 text-center">
                        <div
                            class="w-20 h-20 bg-primary/10 text-primary rounded-[30px] flex items-center justify-center mb-8 animate-bounce-subtle">
                            <CheckCircle class="w-10 h-10" />
                        </div>
                        <p class="text-2xl font-bold italic truncate max-w-lg mb-2">{{
                            selectedFilePath.split('\\').pop()?.split('/').pop() }}</p>
                        <button @click.stop="selectedFilePath = null"
                            class="text-sm font-bold text-primary hover:text-primary/80 transition-colors uppercase tracking-widest mt-4">Change
                            video</button>
                    </div>
                </div>

                <!-- Action -->
                <div v-if="selectedFilePath" class="space-y-8 animate-in slide-in-from-bottom duration-500">
                    <div class="flex items-center justify-between gap-10">
                        <button @click="handleStart" :disabled="store.isProcessing"
                            class="flex-1 py-5 bg-primary text-primary-foreground rounded-[25px] font-black text-xl flex items-center justify-center space-x-4 shadow-2xl shadow-primary/30 hover:shadow-primary/50 hover:-translate-y-1 active:translate-y-0 disabled:opacity-50 disabled:translate-y-0 transition-all duration-300">
                            <Loader2 v-if="store.isProcessing" class="w-7 h-7 animate-spin" />
                            <Play v-else class="w-7 h-7 fill-current" />
                            <span>{{ store.isProcessing ? 'Processing Audio...' : 'Start Production' }}</span>
                        </button>
                        <div class="shrink-0 text-right">
                            <p class="text-sm font-mono uppercase tracking-widest opacity-50 mb-1">{{
                                store.statusMessage || 'System Ready' }}</p>
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
                        Transcription Output
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
                        + {{ store.results.length - 15 }} more segments finalized
                    </p>
                </div>
            </div>

            <!-- Settings Tab -->
            <div v-if="activeTab === 'settings'"
                class="flex-1 p-10 space-y-12 overflow-y-auto custom-scrollbar animate-in slide-in-from-right duration-500">
                <header>
                    <h2 class="text-4xl font-extrabold tracking-tight">Preferences</h2>
                    <p class="text-muted-foreground mt-2 text-lg">Tune the AI engines for your specific workflow.</p>
                </header>

                <div v-if="store.config" class="max-w-3xl space-y-12 pb-32">

                    <section class="space-y-6 bg-card/20 p-8 rounded-[35px] border border-white/5 backdrop-blur-md">
                        <h3 class="text-xs font-black uppercase tracking-[0.2em] text-primary flex items-center">
                            <Database class="w-4 h-4 mr-3" />
                            Large Language Model
                        </h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="md:col-span-2 space-y-2">
                                <label class="text-xs font-bold uppercase opacity-50 ml-1">API Base Endpoint</label>
                                <input v-model="store.config.ai.base_url"
                                    class="w-full px-5 py-4 rounded-2xl bg-background/50 border border-border focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all font-medium" />
                            </div>
                            <div class="md:col-span-2 space-y-2">
                                <label class="text-xs font-bold uppercase opacity-50 ml-1">Secure API
                                    Authorization</label>
                                <input v-model="store.config.ai.api_key" type="password"
                                    class="w-full px-5 py-4 rounded-2xl bg-background/50 border border-border focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all font-medium" />
                            </div>
                            <div class="space-y-2">
                                <label class="text-xs font-bold uppercase opacity-50 ml-1">Active Model</label>
                                <input v-model="store.config.ai.model_name"
                                    class="w-full px-5 py-4 rounded-2xl bg-background/50 border border-border focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all font-medium" />
                            </div>
                            <div class="space-y-2">
                                <label class="text-xs font-bold uppercase opacity-50 ml-1">Batch Integrity</label>
                                <input v-model.number="store.config.ai.batch_size" type="number"
                                    class="w-full px-5 py-4 rounded-2xl bg-background/50 border border-border focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all font-medium" />
                            </div>
                        </div>
                    </section>

                    <section class="space-y-6 bg-card/20 p-8 rounded-[35px] border border-white/5 backdrop-blur-md">
                        <h3 class="text-xs font-black uppercase tracking-[0.2em] text-primary flex items-center">
                            <Cpu class="w-4 h-4 mr-3" />
                            STT Neural Network
                        </h3>
                        <div class="grid grid-cols-2 gap-6">
                            <div class="space-y-2">
                                <label class="text-xs font-bold uppercase opacity-50 ml-1">Parameter Count</label>
                                <select v-model="store.config.whisper.model_size"
                                    class="w-full px-5 py-4 rounded-2xl bg-background/50 border border-border focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all font-bold appearance-none">
                                    <option value="tiny">Tiny (Ultra Fast)</option>
                                    <option value="base">Base</option>
                                    <option value="small">Small</option>
                                    <option value="medium">Medium</option>
                                    <option value="large-v3">Large V3 (Studio Grade)</option>
                                </select>
                            </div>
                            <div class="space-y-2">
                                <label class="text-xs font-bold uppercase opacity-50 ml-1">Compute Core</label>
                                <select v-model="store.config.whisper.device"
                                    class="w-full px-5 py-4 rounded-2xl bg-background/50 border border-border focus:border-primary focus:ring-4 focus:ring-primary/10 outline-none transition-all font-bold appearance-none">
                                    <option value="auto">Auto-detect</option>
                                    <option value="cuda">NVIDIA® CUDA Parallel</option>
                                    <option value="cpu">Generic CPU (Universal)</option>
                                </select>
                            </div>
                        </div>
                    </section>

                    <button @click="saveSettings"
                        class="w-full py-5 bg-foreground text-background rounded-[25px] font-black text-lg shadow-2xl hover:bg-foreground/90 hover:-translate-y-1 active:translate-y-0 transition-all duration-300">
                        Apply Settings
                    </button>
                </div>
            </div>
        </main>
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
    @apply bg-border rounded-full hover:bg-primary/50 transition-colors;
}

.selection\:bg-primary\/30 ::selection {
    background-color: rgba(var(--primary), 0.3);
}
</style>
