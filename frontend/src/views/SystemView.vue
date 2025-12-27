<script setup lang="ts">
import { ref } from 'vue';
import { RefreshCw, Cpu, Database, CheckCircle, AlertTriangle, Download } from 'lucide-vue-next';
import { useAppStore } from '../store/app';

defineProps<{
    t: any;
}>();

const store = useAppStore();
const isCheckingDeps = ref(false);

const handleManualCheck = async () => {
    isCheckingDeps.value = true;
    try {
        await store.checkSystemStatus();
    } finally {
        isCheckingDeps.value = false;
    }
};

const handleInstallDeps = async () => {
    await store.installDependencies();
};
</script>

<template>
    <div class="flex-1 p-10 space-y-12 overflow-y-auto custom-scrollbar animate-in slide-in-from-right duration-500">
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
                    <div class="w-14 h-14 rounded-2xl bg-green-500/20 flex items-center justify-center text-green-500">
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
                    <div class="flex items-center space-x-6 p-6 rounded-3xl bg-amber-500/10 border border-amber-500/20">
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
                        <div class="flex items-center justify-between text-sm font-bold uppercase tracking-widest">
                            <span class="truncate max-w-[80%]">{{ store.statusMessage || t.downloadingCudnn }}</span>
                            <span class="text-primary">{{ Math.round(store.systemStatus.install_progress)
                            }}%</span>
                        </div>
                        <div class="w-full h-3 bg-accent/30 rounded-full overflow-hidden p-1 border border-white/5">
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
                    <div class="w-14 h-14 rounded-2xl bg-blue-500/20 flex items-center justify-center text-blue-500">
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
</template>
