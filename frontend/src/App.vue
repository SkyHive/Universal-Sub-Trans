<script setup lang="ts">
import { ref, onMounted, computed, provide } from 'vue';
import { useAppStore } from './store/app';
import { bridge } from './api/bridge';
import { translations, type Language } from './i18n';

// Components
import TitleBar from './components/TitleBar.vue';
import Sidebar from './components/Sidebar.vue';
import ResumeModal from './components/ResumeModal.vue';

// Views
import TranslateView from './views/TranslateView.vue';
import SettingsView from './views/SettingsView.vue';
import SystemView from './views/SystemView.vue';

const store = useAppStore();
const activeTab = ref('translate');
const currentLang = computed(() => (store.config?.app.language as Language) || 'en');
const t = computed(() => translations[currentLang.value]);

// Resume Logic State
// Resume Logic handled by store

const translateViewRef = ref<any>(null);

onMounted(async () => {
    await store.fetchConfig();
    await store.checkSystemStatus();
    await store.fetchAppInfo();

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
                store.updateInstallProgress(data);
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

const onShowResume = (data: { points: any, path: string }) => {
    store.setResumeState({ show: true, points: data.points, path: data.path });
};

const handleResumeDecision = async (mode: string) => {
    const videoPath = store.pendingVideoPath;
    store.setResumeState({ show: false });
    if (videoPath) {
        await store.startTask(videoPath, currentLang.value === 'zh' ? 'Chinese' : 'English', mode);
    }
};

// Window Dragging Logic
const isDragging = ref(false);
const dragStartPos = ref({ x: 0, y: 0 });
const windowStartPos = ref({ x: 0, y: 0 });

const onDragStart = async (e: MouseEvent) => {
    isDragging.value = true;
    dragStartPos.value = { x: e.screenX, y: e.screenY };
    windowStartPos.value = await bridge.getPosition();
    window.addEventListener('mousemove', onDragging);
    window.addEventListener('mouseup', onDragEnd);
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

// Window Resizing Logic
const isResizing = ref(false);
const resizeStartPos = ref({ x: 0, y: 0 });
const windowStartSize = ref({ width: 0, height: 0 });
const resizeDirection = ref('');

const onResizeStart = async (e: MouseEvent, direction: string) => {
    isResizing.value = true;
    resizeDirection.value = direction;
    resizeStartPos.value = { x: e.screenX, y: e.screenY };
    const size = await bridge.getSize();
    windowStartSize.value = size;
    window.addEventListener('mousemove', onResizing);
    window.addEventListener('mouseup', onResizeEnd);
    e.preventDefault();
};

const onResizing = (e: MouseEvent) => {
    if (isResizing.value) {
        const dpr = window.devicePixelRatio || 1;
        const dx = (e.screenX - resizeStartPos.value.x) / dpr;
        const dy = (e.screenY - resizeStartPos.value.y) / dpr;

        let newWidth = windowStartSize.value.width;
        let newHeight = windowStartSize.value.height;

        if (resizeDirection.value.includes('e')) newWidth += dx;
        if (resizeDirection.value.includes('s')) newHeight += dy;

        // Basic min size enforcement
        newWidth = Math.max(800, newWidth);
        newHeight = Math.max(600, newHeight);

        // Round to integer to avoid potential precision issues with backend
        bridge.resizeWindow(Math.round(newWidth), Math.round(newHeight));
    }
};

const onResizeEnd = () => {
    isResizing.value = false;
    window.removeEventListener('mousemove', onResizing);
    window.removeEventListener('mouseup', onResizeEnd);
};
</script>

<template>
    <div
        class="flex h-screen bg-background text-foreground transition-colors duration-300 dark overflow-hidden selection:bg-primary/30">

        <!-- Custom Resize Handles -->
        <div class="fixed right-0 top-0 bottom-0 w-1.5 cursor-ew-resize z-[200] hover:bg-primary/10 transition-colors"
            @mousedown="onResizeStart($event, 'e')"></div>
        <div class="fixed left-0 right-0 bottom-0 h-1.5 cursor-ns-resize z-[200] hover:bg-primary/10 transition-colors"
            @mousedown="onResizeStart($event, 's')"></div>
        <div class="fixed right-0 bottom-0 w-4 h-4 cursor-nwse-resize z-[201] hover:bg-primary/20 transition-colors"
            @mousedown="onResizeStart($event, 'se')"></div>

        <TitleBar @drag-begin="onDragStart" />

        <Sidebar v-model:activeTab="activeTab" :t="t" />

        <!-- Main Content -->
        <main
            class="flex-1 flex flex-col overflow-hidden bg-gradient-to-br from-background via-background to-primary/5 pt-10">

            <TranslateView v-if="activeTab === 'translate'" ref="translateViewRef" :t="t" :currentLang="currentLang"
                @showResume="onShowResume" />

            <SettingsView v-if="activeTab === 'settings'" :t="t" />

            <SystemView v-if="activeTab === 'system'" :t="t" />
        </main>

        <ResumeModal :show="store.showResumeModal" :resumePoints="store.resumePoints" :t="t"
            @decision="handleResumeDecision" @close="store.setResumeState({ show: false })" />
    </div>
</template>

<style>
/* Remove problematic -webkit-app-region styles that interfere with selection */
.drag-region {
    cursor: grab;
}

.drag-region:active {
    cursor: grabbing;
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
