<script setup lang="ts">
import { Globe, FileVideo, Settings as SettingsIcon, Monitor, Cpu, Database } from 'lucide-vue-next';
import { useAppStore } from '../store/app';

defineProps<{
    activeTab: string;
    t: any;
}>();

defineEmits<{
    (e: 'update:activeTab', value: string): void;
}>();

const store = useAppStore();
</script>

<template>
    <aside class="w-64 border-r border-border bg-card/50 backdrop-blur-3xl flex flex-col p-6 pt-10 space-y-8 relative">
        <div class="flex items-center space-x-3 mb-4">
            <div
                class="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-primary-foreground shadow-lg shadow-primary/20">
                <Globe class="w-6 h-6" />
            </div>
            <h1 class="text-xl font-bold tracking-tight">UniSub</h1>
        </div>

        <nav class="flex-1 space-y-1">
            <button @click="$emit('update:activeTab', 'translate')" :class="[
                'w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 group',
                activeTab === 'translate' ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/10' : 'hover:bg-accent/50 text-muted-foreground hover:text-foreground'
            ]">
                <FileVideo class="w-5 h-5 transition-transform group-hover:scale-110" />
                <span class="font-medium">{{ t.translate }}</span>
            </button>
            <button @click="$emit('update:activeTab', 'settings')" :class="[
                'w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 group',
                activeTab === 'settings' ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/10' : 'hover:bg-accent/50 text-muted-foreground hover:text-foreground'
            ]">
                <SettingsIcon class="w-5 h-5 transition-transform group-hover:rotate-45" />
                <span class="font-medium">{{ t.settings }}</span>
            </button>
            <button @click="$emit('update:activeTab', 'system')" :class="[
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
</template>
