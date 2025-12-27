<script setup lang="ts">
import { Database, CheckCircle, Play, Loader2 } from 'lucide-vue-next';

defineProps<{
    show: boolean;
    resumePoints: { has_audio: boolean, has_transcript: boolean } | null;
    t: any;
}>();

const emit = defineEmits<{
    (e: 'decision', mode: string): void;
    (e: 'close'): void;
}>();
</script>

<template>
    <div v-if="show"
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
                <button v-if="resumePoints?.has_transcript" @click="emit('decision', 'use_transcript')"
                    class="w-full p-6 rounded-3xl bg-primary text-primary-foreground hover:scale-[1.02] active:scale-100 transition-all text-left flex items-center space-x-4">
                    <CheckCircle class="w-8 h-8 opacity-60" />
                    <div>
                        <p class="font-bold">{{ t.resumeTrans }}</p>
                        <p class="text-xs opacity-70">{{ t.skipStt }}</p>
                    </div>
                </button>

                <button v-if="resumePoints?.has_audio" @click="emit('decision', 'use_audio')"
                    class="w-full p-6 rounded-3xl bg-accent text-foreground hover:scale-[1.02] active:scale-100 transition-all text-left flex items-center space-x-4">
                    <Play class="w-8 h-8 opacity-60" />
                    <div>
                        <p class="font-bold">{{ t.useExistingAudio }}</p>
                        <p class="text-xs opacity-70">{{ t.rerunStt }}</p>
                    </div>
                </button>

                <button @click="emit('decision', 'fresh')"
                    class="w-full p-6 rounded-3xl border border-white/5 hover:bg-white/5 transition-all text-left flex items-center space-x-4">
                    <Loader2 class="w-8 h-8 opacity-40" />
                    <div>
                        <p class="font-bold opacity-60">{{ t.startFresh }}</p>
                        <p class="text-xs opacity-40">{{ t.cleanTemp }}</p>
                    </div>
                </button>

                <button @click="emit('close')"
                    class="w-full py-4 text-xs font-bold uppercase tracking-widest opacity-30 hover:opacity-100">{{
                        t.cancel }}</button>
            </div>
        </div>
    </div>
</template>
