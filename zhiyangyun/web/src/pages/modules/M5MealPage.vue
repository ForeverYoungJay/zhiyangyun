<template>
  <div class="page-shell">
    <div class="page-title">
      <div>
        <h2>A1-M5 膳食管理</h2>
        <div class="desc">膳食方案+下发联动，支持分页搜索、自动联想与姓名展示（替代ID）。</div>
      </div>
      <el-space>
        <el-button @click="loadAll">刷新</el-button>
        <el-button type="primary" @click="planDrawer = true">新建方案</el-button>
        <el-button type="success" @click="orderDrawer = true">下发膳食</el-button>
      </el-space>
    </div>

    <el-card class="zy-card">
      <template #header>膳食方案列表</template>
      <el-form inline>
        <el-form-item label="关键字">
          <el-input v-model="planQuery.keyword" placeholder="方案名/营养标签" clearable @change="searchPlans" />
        </el-form-item>
        <el-form-item label="餐次">
          <el-select v-model="planQuery.meal_type" placeholder="全部" clearable style="width:140px" @change="searchPlans">
            <el-option label="早餐" value="breakfast" />
            <el-option label="午餐" value="lunch" />
            <el-option label="晚餐" value="dinner" />
          </el-select>
        </el-form-item>
      </el-form>
      <el-table :data="plans" border>
        <el-table-column prop="name" label="方案名称" min-width="140" />
        <el-table-column prop="plan_date" label="日期" min-width="120" />
        <el-table-column prop="meal_type" label="餐次" min-width="100" />
        <el-table-column prop="nutrition_tag" label="营养标签" min-width="120" />
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:12px">
        <el-pagination v-model:current-page="planQuery.page" v-model:page-size="planQuery.page_size" :total="planTotal" layout="total, sizes, prev, pager, next" @current-change="loadPlans" @size-change="searchPlans" />
      </div>
    </el-card>

    <el-card class="zy-card" style="margin-top:16px">
      <template #header>膳食下发记录</template>
      <el-form inline>
        <el-form-item label="关键字">
          <el-input v-model="orderQuery.keyword" placeholder="姓名/编号/方案" clearable @change="searchOrders" />
        </el-form-item>
      </el-form>
      <el-table :data="orders" border>
        <el-table-column prop="elder_name" label="长者姓名" min-width="120" />
        <el-table-column prop="elder_no" label="长者编号" min-width="130" />
        <el-table-column prop="plan_name" label="膳食方案" min-width="140" />
        <el-table-column prop="meal_type" label="餐次" min-width="100" />
        <el-table-column prop="nutrition_tag" label="营养标签" min-width="120" />
        <el-table-column prop="status" label="状态" min-width="100" />
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:12px">
        <el-pagination v-model:current-page="orderQuery.page" v-model:page-size="orderQuery.page_size" :total="orderTotal" layout="total, sizes, prev, pager, next" @current-change="loadOrders" @size-change="searchOrders" />
      </div>
    </el-card>

    <el-drawer v-model="planDrawer" title="新建膳食方案" size="500px" destroy-on-close>
      <el-form ref="planFormRef" :model="planForm" :rules="planRules" label-width="100px">
        <el-form-item label="方案名称" prop="name"><el-input v-model="planForm.name" /></el-form-item>
        <el-form-item label="计划日期" prop="plan_date"><el-date-picker v-model="planForm.plan_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="餐次" prop="meal_type">
          <el-select v-model="planForm.meal_type" style="width:100%">
            <el-option label="早餐" value="breakfast" />
            <el-option label="午餐" value="lunch" />
            <el-option label="晚餐" value="dinner" />
          </el-select>
        </el-form-item>
        <el-form-item label="营养标签" prop="nutrition_tag"><el-input v-model="planForm.nutrition_tag" placeholder="如：低盐/高蛋白" /></el-form-item>
      </el-form>
      <template #footer><el-button type="primary" @click="createPlan">提交</el-button></template>
    </el-drawer>

    <el-drawer v-model="orderDrawer" title="下发膳食订单" size="500px" destroy-on-close>
      <el-form ref="orderFormRef" :model="orderForm" :rules="orderRules" label-width="100px">
        <el-form-item label="长者" prop="elder_id">
          <el-autocomplete v-model="elderKeyword" :fetch-suggestions="queryElders" value-key="label" placeholder="输入姓名/编号搜索" @select="onElderSelect" style="width:100%" clearable />
          <div style="font-size:12px;color:#909399;margin-top:4px">已选：{{ selectedElderName || '未选择' }}</div>
        </el-form-item>
        <el-form-item label="膳食方案" prop="plan_id">
          <el-select v-model="orderForm.plan_id" filterable clearable style="width:100%" placeholder="请选择方案">
            <el-option v-for="p in planOptions" :key="p.id" :label="`${p.name}（${p.plan_date} ${p.meal_type}）`" :value="p.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer><el-button type="primary" @click="createOrder">提交</el-button></template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const plans = ref<any[]>([])
const orders = ref<any[]>([])
const planOptions = ref<any[]>([])
const planTotal = ref(0)
const orderTotal = ref(0)
const planDrawer = ref(false)
const orderDrawer = ref(false)
const planFormRef = ref<FormInstance>()
const orderFormRef = ref<FormInstance>()
const elderKeyword = ref('')
const selectedElderName = ref('')

const planQuery = reactive({ page: 1, page_size: 10, keyword: '', meal_type: '' })
const orderQuery = reactive({ page: 1, page_size: 10, keyword: '', status: '' })
const planForm = reactive({ name: '', plan_date: '', meal_type: 'lunch', nutrition_tag: '', note: '' })
const orderForm = reactive({ elder_id: '', plan_id: '' })

const planRules: FormRules = {
  name: [{ required: true, message: '请填写方案名称', trigger: 'blur' }],
  plan_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  meal_type: [{ required: true, message: '请选择餐次', trigger: 'change' }],
  nutrition_tag: [{ required: true, message: '请填写营养标签', trigger: 'blur' }]
}
const orderRules: FormRules = {
  elder_id: [{ required: true, message: '请选择长者', trigger: 'change' }],
  plan_id: [{ required: true, message: '请选择膳食方案', trigger: 'change' }]
}

const loadPlans = async () => {
  const resp = await http.get('/m5-meal/plans', { params: planQuery })
  const data = resp.data.data || {}
  plans.value = data.items || []
  planTotal.value = data.total || 0
  planOptions.value = data.items || []
}

const loadOrders = async () => {
  const resp = await http.get('/m5-meal/orders', { params: orderQuery })
  const data = resp.data.data || {}
  orders.value = data.items || []
  orderTotal.value = data.total || 0
}

const searchPlans = async () => { planQuery.page = 1; await loadPlans() }
const searchOrders = async () => { orderQuery.page = 1; await loadOrders() }
const loadAll = async () => { await Promise.all([loadPlans(), loadOrders()]) }

const queryElders = async (keyword: string, cb: (items: any[]) => void) => {
  const resp = await http.get('/m5-meal/elders/suggest', { params: { keyword, limit: 20 } })
  const list = (resp.data.data || []).map((x: any) => ({ ...x, value: x.id, label: `${x.name}（${x.elder_no}）` }))
  cb(list)
}

const onElderSelect = (item: any) => {
  orderForm.elder_id = item.id
  elderKeyword.value = item.label
  selectedElderName.value = item.name
}

const createPlan = async () => {
  await planFormRef.value?.validate()
  await http.post('/m5-meal/plans', planForm)
  ElMessage.success('方案创建成功')
  planDrawer.value = false
  await loadPlans()
}

const createOrder = async () => {
  await orderFormRef.value?.validate()
  await http.post('/m5-meal/orders', orderForm)
  ElMessage.success('下发成功，已同步计费')
  orderDrawer.value = false
  orderForm.elder_id = ''
  orderForm.plan_id = ''
  elderKeyword.value = ''
  selectedElderName.value = ''
  await loadOrders()
}

onMounted(loadAll)
</script>
