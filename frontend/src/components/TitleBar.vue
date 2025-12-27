<script setup lang="ts">
import { Minus, X } from 'lucide-vue-next';
import { bridge } from '../api/bridge';

const emit = defineEmits<{
    (e: 'drag-begin', event: MouseEvent): void;
}>();

const handleMinimize = () => bridge.minimize();
const handleClose = () => bridge.close();
const handleMouseDown = (e: MouseEvent) => {
    emit('drag-begin', e);
};
</script>

<template>
    <!-- Custom Title Bar (Only for Frameless) -->
    <div class="fixed top-0 left-0 right-0 h-10 z-[100] flex items-center justify-between pointer-events-none">
        <div class="flex-1 h-full drag-region pointer-events-auto" @mousedown="handleMouseDown"></div>
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
</template>
