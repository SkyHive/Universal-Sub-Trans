<script setup lang="ts">
import { ref } from 'vue';
import { Database, Cpu, Globe, Loader2 } from 'lucide-vue-next';
import { useAppStore } from '../store/app';

const props = defineProps<{
    t: any;
}>();

const store = useAppStore();

// Settings feedback state
const saveStatus = ref<'idle' | 'saving' | 'success' | 'error'>('idle');
const saveMessage = ref('');

const saveSettings = async () => {
    if (store.config) {
        saveStatus.value = 'saving';
        try {
            await store.saveConfig(store.config);
            saveStatus.value = 'success';
            saveMessage.value = props.t.settingsSaved;
        } catch (err) {
            saveStatus.value = 'error';
            saveMessage.value = props.t.settingsError;
        }
        setTimeout(() => {
            saveStatus.value = 'idle';
        }, 3000);
    }
};
</script>

<template>
    <div class="flex-1 p-10 space-y-12 overflow-y-auto custom-scrollbar animate-in slide-in-from-right duration-500">
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

                <div v-if="saveStatus !== 'idle' && saveStatus !== 'saving'" :class="['text-center text-sm font-bold p-4 rounded-2xl transition-all duration-500 animate-in fade-in slide-in-from-top-4',
                    saveStatus === 'success' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500']">
                    {{ saveMessage }}
                </div>
            </div>
        </div>
    </div>
</template>
