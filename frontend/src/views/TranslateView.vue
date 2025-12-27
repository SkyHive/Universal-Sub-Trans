<script setup lang="ts">
import { ref } from 'vue';
import { FileVideo, CheckCircle, Play, Loader2 } from 'lucide-vue-next';
import { useAppStore } from '../store/app';
import { bridge } from '../api/bridge';

const props = defineProps<{
    t: any;
    currentLang: string;
}>();

const emit = defineEmits<{
    (e: 'showResume', points: any): void;
}>();

const store = useAppStore();
const selectedFilePath = ref<string | null>(null);

const handleSelectFile = async () => {
    const path = await bridge.selectFile();
    if (path) {
        selectedFilePath.value = path;
    }
};

const handleStart = async () => {
    if (!selectedFilePath.value) return;

    // Check if we can resume
    const points = await store.checkResumePoint(selectedFilePath.value);
    if (points.has_audio || points.has_transcript) {
        emit('showResume', { points, path: selectedFilePath.value });
    } else {
        await store.startTask(selectedFilePath.value, props.currentLang === 'zh' ? 'Chinese' : 'English', "fresh");
    }
};

defineExpose({
    selectedFilePath,
    handleStart
});
</script>

<template>
    <div class="flex-1 flex flex-col p-10 space-y-10 overflow-y-auto custom-scrollbar">
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
                    <p v-if="store.isProcessing" class="text-5xl font-black tabular-nums tracking-tighter text-primary">
                        {{
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
</template>
