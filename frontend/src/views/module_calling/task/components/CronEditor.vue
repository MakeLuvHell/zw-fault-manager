<!-- Cron 表达式可视化编辑器 - 下拉选择版 -->
<template>
  <div class="cron-editor">
    <!-- 表达式预览 -->
    <div class="cron-preview">
      <div class="preview-label">
        <el-icon><Clock /></el-icon>
        <span>执行计划</span>
      </div>
      <div class="preview-content">
        <el-tag type="primary" size="large" effect="dark">{{ cronDescription }}</el-tag>
      </div>
    </div>

    <!-- 配置区域 -->
    <div class="cron-config">
      <!-- 第一行：执行类型 -->
      <div class="config-row">
        <div class="config-item">
          <span class="item-label">执行周期</span>
          <el-select v-model="cronType" placeholder="选择执行周期" @change="handleTypeChange">
            <el-option label="每天执行" value="daily" />
            <el-option label="每周执行" value="weekly" />
            <el-option label="每月执行" value="monthly" />
            <el-option label="工作日执行" value="workday" />
            <el-option label="间隔执行" value="interval" />
            <el-option label="自定义" value="custom" />
          </el-select>
        </div>
      </div>

      <!-- 每周：选择星期 -->
      <div class="config-row" v-if="cronType === 'weekly'">
        <div class="config-item full-width">
          <span class="item-label">执行日</span>
          <el-select v-model="weekDays" multiple placeholder="选择星期" @change="updateCron">
            <el-option
              v-for="(day, index) in weekDayOptions"
              :key="index"
              :label="day"
              :value="index"
            />
          </el-select>
        </div>
      </div>

      <!-- 每月：选择日期 -->
      <div class="config-row" v-if="cronType === 'monthly'">
        <div class="config-item">
          <span class="item-label">执行日</span>
          <el-select v-model="monthDay" placeholder="选择日期" @change="updateCron">
            <el-option
              v-for="d in 31"
              :key="d"
              :label="`${d}号`"
              :value="d"
            />
          </el-select>
        </div>
      </div>

      <!-- 间隔执行：间隔值和单位 -->
      <div class="config-row" v-if="cronType === 'interval'">
        <div class="config-item">
          <span class="item-label">间隔时间</span>
          <div class="interval-group">
            <el-select v-model="intervalValue" placeholder="间隔" style="width: 100px" @change="updateCron">
              <el-option v-for="n in 60" :key="n" :label="n" :value="n" />
            </el-select>
            <el-select v-model="intervalUnit" placeholder="单位" style="width: 90px" @change="updateCron">
              <el-option label="分钟" value="minute" />
              <el-option label="小时" value="hour" />
            </el-select>
          </div>
        </div>
        <div class="config-item" v-if="intervalUnit === 'minute'">
          <span class="item-label">时段限制</span>
          <div class="time-range-group">
            <el-select v-model="startHour" placeholder="起始" @change="updateCron">
              <el-option v-for="h in 24" :key="h-1" :label="`${h-1}时`" :value="h-1" />
            </el-select>
            <span class="range-separator">至</span>
            <el-select v-model="endHour" placeholder="结束" @change="updateCron">
              <el-option v-for="h in 24" :key="h-1" :label="`${h-1}时`" :value="h-1" />
            </el-select>
          </div>
        </div>
      </div>

      <!-- 执行时间：小时和分钟 (非间隔模式) -->
      <div class="config-row" v-if="cronType !== 'interval' && cronType !== 'custom'">
        <div class="config-item">
          <span class="item-label">执行时间</span>
          <div class="time-group">
            <el-select v-model="hour" placeholder="时" @change="updateCron">
              <el-option v-for="h in 24" :key="h-1" :label="`${h-1}时`" :value="h-1" />
            </el-select>
            <span class="time-separator">:</span>
            <el-select v-model="minute" placeholder="分" @change="updateCron">
              <el-option v-for="m in 60" :key="m-1" :label="`${(m-1).toString().padStart(2, '0')}分`" :value="m-1" />
            </el-select>
          </div>
        </div>
      </div>

      <!-- 自定义模式 -->
      <div class="config-row custom-mode" v-if="cronType === 'custom'">
        <div class="config-item">
          <span class="item-label">秒</span>
          <el-select v-model="customSecond" placeholder="秒" @change="updateCron">
            <el-option label="每秒 (*)" value="*" />
            <el-option label="0秒" value="0" />
            <el-option v-for="s in [15, 30, 45]" :key="s" :label="`${s}秒`" :value="String(s)" />
          </el-select>
        </div>
        <div class="config-item">
          <span class="item-label">分</span>
          <el-select v-model="customMinute" placeholder="分" @change="updateCron">
            <el-option label="每分 (*)" value="*" />
            <el-option v-for="m in 60" :key="m-1" :label="`${m-1}分`" :value="String(m-1)" />
            <el-option v-for="i in [5, 10, 15, 30]" :key="`i${i}`" :label="`每${i}分`" :value="`*/${i}`" />
          </el-select>
        </div>
        <div class="config-item">
          <span class="item-label">时</span>
          <el-select v-model="customHour" placeholder="时" @change="updateCron">
            <el-option label="每时 (*)" value="*" />
            <el-option-group label="固定时间">
              <el-option v-for="h in 24" :key="h-1" :label="`${h-1}时`" :value="String(h-1)" />
            </el-option-group>
            <el-option-group label="时间范围">
              <el-option label="工作时段 (9-18时)" value="9-18" />
              <el-option label="上午 (8-12时)" value="8-12" />
              <el-option label="下午 (15-18时)" value="15-18" />
              <el-option label="晚间 (18-22时)" value="18-22" />
              <el-option label="白天 (6-22时)" value="6-22" />
            </el-option-group>
            <el-option-group label="间隔执行">
              <el-option v-for="i in [2, 3, 4, 6, 8, 12]" :key="`i${i}`" :label="`每${i}小时`" :value="`*/${i}`" />
            </el-option-group>
          </el-select>
        </div>
      </div>

      <div class="config-row custom-mode" v-if="cronType === 'custom'">
        <div class="config-item">
          <span class="item-label">日</span>
          <el-select v-model="customDay" placeholder="日" @change="updateCron">
            <el-option label="每日 (*)" value="*" />
            <el-option v-for="d in 31" :key="d" :label="`${d}号`" :value="String(d)" />
          </el-select>
        </div>
        <div class="config-item">
          <span class="item-label">月</span>
          <el-select v-model="customMonth" placeholder="月" @change="updateCron">
            <el-option label="每月 (*)" value="*" />
            <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="String(m)" />
          </el-select>
        </div>
        <div class="config-item">
          <span class="item-label">周</span>
          <el-select v-model="customWeek" placeholder="周" @change="updateCron">
            <el-option label="不限 (*)" value="*" />
            <el-option label="工作日" value="1-5" />
            <el-option label="周末" value="0,6" />
            <el-option
              v-for="(day, index) in weekDayOptions"
              :key="index"
              :label="day"
              :value="String(index)"
            />
          </el-select>
        </div>
      </div>
    </div>

    <!-- 表达式显示 -->
    <div class="cron-expression">
      <span class="expr-label">Cron 表达式:</span>
      <code class="expr-value">{{ modelValue || '未配置' }}</code>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { Clock } from "@element-plus/icons-vue";

defineOptions({
  name: "CronEditor",
});

const props = defineProps<{
  modelValue: string;
}>();

const emit = defineEmits<{
  (e: "update:modelValue", value: string): void;
}>();

// 执行类型
const cronType = ref("daily");

// 通用配置
const hour = ref(9);
const minute = ref(0);
const weekDays = ref<number[]>([1, 2, 3, 4, 5]);
const monthDay = ref(1);

// 间隔配置
const intervalValue = ref(30);
const intervalUnit = ref("minute");
const startHour = ref(9);
const endHour = ref(18);

// 自定义配置
const customSecond = ref("0");
const customMinute = ref("0");
const customHour = ref("9");
const customDay = ref("*");
const customMonth = ref("*");
const customWeek = ref("*");

const weekDayOptions = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];

// 描述
const cronDescription = computed(() => {
  if (!props.modelValue) return "请配置执行时间";

  switch (cronType.value) {
    case "daily":
      return `每天 ${hour.value}:${minute.value.toString().padStart(2, "0")} 执行`;
    case "weekly":
      const days = weekDays.value.map(d => weekDayOptions[d]).join("、");
      return `每周${days} ${hour.value}:${minute.value.toString().padStart(2, "0")} 执行`;
    case "monthly":
      return `每月${monthDay.value}号 ${hour.value}:${minute.value.toString().padStart(2, "0")} 执行`;
    case "workday":
      return `工作日 ${hour.value}:${minute.value.toString().padStart(2, "0")} 执行`;
    case "interval":
      if (intervalUnit.value === "minute") {
        return `${startHour.value}-${endHour.value}时 每${intervalValue.value}分钟执行`;
      }
      return `每${intervalValue.value}小时执行`;
    case "custom":
      return "自定义执行计划";
    default:
      return props.modelValue;
  }
});

// 类型变更
function handleTypeChange() {
  updateCron();
}

// 更新 Cron 表达式
function updateCron() {
  let expression = "";

  switch (cronType.value) {
    case "daily":
      expression = `0 ${minute.value} ${hour.value} * * *`;
      break;
    case "weekly":
      if (weekDays.value.length > 0) {
        expression = `0 ${minute.value} ${hour.value} * * ${weekDays.value.sort().join(",")}`;
      }
      break;
    case "monthly":
      expression = `0 ${minute.value} ${hour.value} ${monthDay.value} * *`;
      break;
    case "workday":
      expression = `0 ${minute.value} ${hour.value} * * 1-5`;
      break;
    case "interval":
      if (intervalUnit.value === "minute") {
        expression = `0 */${intervalValue.value} ${startHour.value}-${endHour.value} * * *`;
      } else {
        expression = `0 0 */${intervalValue.value} * * *`;
      }
      break;
    case "custom":
      expression = `${customSecond.value} ${customMinute.value} ${customHour.value} ${customDay.value} ${customMonth.value} ${customWeek.value}`;
      break;
  }

  if (expression) {
    emit("update:modelValue", expression);
  }
}

// 解析表达式
function parseExpression(cron: string) {
  if (!cron) return;

  const parts = cron.split(" ");
  if (parts.length < 6) return;

  const [sec, min, hr, day, month, week] = parts;

  // 自定义配置赋值
  customSecond.value = sec;
  customMinute.value = min;
  customHour.value = hr;
  customDay.value = day;
  customMonth.value = month;
  customWeek.value = week;

  // 识别模式
  if (week === "1-5" && day === "*" && month === "*" && !min.includes("/") && !hr.includes("/")) {
    cronType.value = "workday";
    hour.value = parseInt(hr) || 9;
    minute.value = parseInt(min) || 0;
  } else if (week !== "*" && week !== "1-5" && day === "*" && month === "*") {
    cronType.value = "weekly";
    weekDays.value = week.split(",").map(d => parseInt(d)).filter(d => !isNaN(d));
    hour.value = parseInt(hr) || 9;
    minute.value = parseInt(min) || 0;
  } else if (day !== "*" && month === "*" && week === "*") {
    cronType.value = "monthly";
    monthDay.value = parseInt(day) || 1;
    hour.value = parseInt(hr) || 9;
    minute.value = parseInt(min) || 0;
  } else if (min.includes("/") || hr.includes("/")) {
    cronType.value = "interval";
    if (min.includes("/")) {
      intervalUnit.value = "minute";
      intervalValue.value = parseInt(min.split("/")[1]) || 30;
      if (hr.includes("-")) {
        const [s, e] = hr.split("-");
        startHour.value = parseInt(s) || 9;
        endHour.value = parseInt(e) || 18;
      }
    } else {
      intervalUnit.value = "hour";
      intervalValue.value = parseInt(hr.split("/")[1]) || 1;
    }
  } else if (week === "*" && day === "*" && month === "*" && !min.includes("/") && !hr.includes("/")) {
    cronType.value = "daily";
    hour.value = parseInt(hr) || 9;
    minute.value = parseInt(min) || 0;
  } else {
    cronType.value = "custom";
  }
}

// 监听外部值
watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal) {
      parseExpression(newVal);
    }
  },
  { immediate: true }
);

// 初始化
onMounted(() => {
  if (!props.modelValue) {
    updateCron();
  }
});
</script>

<style scoped>
.cron-editor {
  width: 100%;
  background: var(--el-bg-color-page);
  border-radius: 8px;
  padding: 16px;
}

.cron-preview {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: linear-gradient(135deg, var(--el-color-primary-light-9), var(--el-color-primary-light-7));
  border-radius: 8px;
  margin-bottom: 16px;
}

.preview-label {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--el-color-primary);
  font-weight: 500;
}

.preview-content {
  flex: 1;
}

.cron-config {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.config-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.config-row.custom-mode {
  gap: 12px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 140px;
}

.config-item.full-width {
  flex: 1;
  min-width: 100%;
}

.item-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  font-weight: 500;
}

.time-group,
.interval-group,
.time-range-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-separator,
.range-separator {
  color: var(--el-text-color-placeholder);
  font-size: 14px;
}

.cron-expression {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 10px 12px;
  background: var(--el-fill-color);
  border-radius: 6px;
  border: 1px dashed var(--el-border-color);
}

.expr-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.expr-value {
  font-family: "Fira Code", "Monaco", "Consolas", monospace;
  font-size: 13px;
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  padding: 2px 8px;
  border-radius: 4px;
}

/* 自定义模式下的紧凑布局 */
.custom-mode .config-item {
  min-width: 100px;
  flex: 1;
}

/* 响应式 */
@media (max-width: 768px) {
  .config-row {
    flex-direction: column;
  }
  
  .config-item {
    width: 100%;
  }
}
</style>
