<template>
  <div class="page-shell">
    <div class="page-title">
      <div>
        <h2>B2 家属门户闭环</h2>
        <div class="desc">家属互动/通知 + 账单/记录/问卷，统一分页搜索筛选与姓名化展示。</div>
      </div>
    </div>

    <el-row :gutter="16">
      <el-col :span="8">
        <el-card class="zy-card">
          <template #header>家属账号</template>
          <el-form label-width="90px">
            <el-form-item label="关联长者"><el-select v-model="form.elder_id" style="width:100%"><el-option v-for="e in elders" :key="e.id" :label="e.name" :value="e.id" /></el-select></el-form-item>
            <el-form-item label="家属姓名"><el-input v-model="form.name" /></el-form-item>
            <el-form-item label="手机号"><el-input v-model="form.phone" /></el-form-item>
            <el-form-item label="关系"><el-select v-model="form.relation" style="width:100%"><el-option label="子女" value="子女"/><el-option label="配偶" value="配偶"/><el-option label="其他" value="其他"/></el-select></el-form-item>
            <el-button type="primary" @click="createFamily">新增家属</el-button>
          </el-form>
          <el-form inline style="margin-top:10px">
            <el-form-item><el-input v-model="familyQuery.keyword" clearable placeholder="姓名/手机号/长者" @change="loadFamilies"/></el-form-item>
            <el-form-item><el-select v-model="familyQuery.relation" clearable placeholder="关系" @change="loadFamilies"><el-option label="子女" value="子女"/><el-option label="配偶" value="配偶"/><el-option label="其他" value="其他"/></el-select></el-form-item>
          </el-form>
          <el-table :data="families" border @row-click="pickElderByFamily">
            <el-table-column prop="name" label="家属"/>
            <el-table-column prop="relation" label="关系"/>
            <el-table-column prop="elder_name" label="长者姓名"/>
          </el-table>
          <div style="display:flex;justify-content:flex-end;margin-top:8px"><el-pagination v-model:current-page="familyQuery.page" v-model:page-size="familyQuery.page_size" :total="familyTotal" layout="total, prev, pager, next" @current-change="loadFamilies" @size-change="loadFamilies" /></div>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card class="zy-card">
          <template #header>家属门户数据</template>
          <div style="margin-bottom:10px"><el-select v-model="selectedElderId" placeholder="选择长者" style="width:260px" @change="loadElderPortalData"><el-option v-for="e in elders" :key="e.id" :label="e.name" :value="e.id" /></el-select></div>

          <el-tabs>
            <el-tab-pane label="长者总览">
              <el-descriptions v-if="elderOverview" :column="2" border>
                <el-descriptions-item label="长者姓名">{{ elderOverview.elder?.name }}</el-descriptions-item>
                <el-descriptions-item label="护理等级">{{ elderOverview.elder?.care_level }}</el-descriptions-item>
                <el-descriptions-item label="在院状态">{{ elderOverview.elder?.status }}</el-descriptions-item>
                <el-descriptions-item label="生效套餐数">{{ elderOverview.active_packages }}</el-descriptions-item>
              </el-descriptions>
            </el-tab-pane>
            <el-tab-pane label="服务增购">
              <el-form inline>
                <el-form-item label="护理套餐"><el-select v-model="serviceOrder.package_id" style="width:260px"><el-option v-for="p in serviceCatalog.packages" :key="p.id" :label="`${p.name}（${p.period}）`" :value="p.id" /></el-select></el-form-item>
                <el-button type="primary" @click="placeServiceOrder">立即下单</el-button>
              </el-form>
              <el-table :data="serviceCatalog.items" border style="margin-top:10px"><el-table-column prop="name" label="项目"/><el-table-column prop="category" label="类别"/><el-table-column prop="unit_price" label="单价"/></el-table>
            </el-tab-pane>
            <el-tab-pane label="账单明细">
              <el-form inline><el-form-item><el-input v-model="billQuery.keyword" clearable placeholder="项目关键字" @change="loadElderPortalData"/></el-form-item><el-form-item><el-select v-model="billQuery.status" clearable placeholder="状态" @change="loadElderPortalData"><el-option label="unpaid" value="unpaid"/><el-option label="partial" value="partial"/><el-option label="paid" value="paid"/></el-select></el-form-item></el-form>
              <el-table :data="bills" border><el-table-column prop="item_name" label="项目"/><el-table-column prop="amount" label="金额"/><el-table-column prop="charged_on" label="扣费日期"/><el-table-column prop="status" label="状态"/></el-table>
              <div style="display:flex;justify-content:flex-end;margin-top:8px"><el-pagination v-model:current-page="billQuery.page" v-model:page-size="billQuery.page_size" :total="billTotal" layout="total, prev, pager, next" @current-change="loadElderPortalData" @size-change="loadElderPortalData" /></div>
            </el-tab-pane>
            <el-tab-pane label="护理记录">
              <el-form inline><el-form-item><el-input v-model="recordQuery.keyword" clearable placeholder="记录关键字" @change="loadElderPortalData"/></el-form-item></el-form>
              <el-table :data="careRecords" border><el-table-column prop="content" label="内容"/><el-table-column prop="occurred_at" label="时间"/></el-table>
            </el-tab-pane>
            <el-tab-pane label="问卷评价">
              <el-form inline><el-form-item label="评分"><el-rate v-model="survey.score" /></el-form-item><el-form-item><el-input v-model="survey.comment" placeholder="请填写评价" style="width:320px"/></el-form-item><el-button type="primary" @click="submitSurvey">提交</el-button></el-form>
              <el-table :data="surveys" border style="margin-top:10px"><el-table-column prop="score" label="评分"/><el-table-column prop="comment" label="评价"/><el-table-column prop="created_at" label="时间"/></el-table>
            </el-tab-pane>
            <el-tab-pane label="互动通知">
              <el-form inline><el-form-item><el-input v-model="notifyQuery.keyword" clearable placeholder="标题/内容" @change="loadNotifications"/></el-form-item></el-form>
              <el-table :data="notifications" border><el-table-column prop="title" label="标题"/><el-table-column prop="content" label="内容"/><el-table-column prop="sent_at" label="时间"/></el-table>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const elders = ref<any[]>([])
const families = ref<any[]>([])
const familyTotal = ref(0)
const bills = ref<any[]>([])
const billTotal = ref(0)
const careRecords = ref<any[]>([])
const surveys = ref<any[]>([])
const notifications = ref<any[]>([])
const serviceCatalog = ref<any>({ items: [], packages: [] })
const elderOverview = ref<any>(null)
const selectedElderId = ref('')

const form = reactive({ elder_id: '', name: '', phone: '', relation: '' })
const survey = reactive({ score: 5, comment: '' })
const serviceOrder = reactive({ package_id: '' })
const familyQuery = reactive({ page: 1, page_size: 10, keyword: '', relation: '' })
const billQuery = reactive({ page: 1, page_size: 10, keyword: '', status: '' })
const recordQuery = reactive({ page: 1, page_size: 10, keyword: '' })
const notifyQuery = reactive({ page: 1, page_size: 10, keyword: '' })

const loadFamilies = async () => {
  const resp = (await http.get('/b2-family/accounts', { params: familyQuery })).data.data || {}
  families.value = resp.items || []
  familyTotal.value = resp.total || 0
}

const loadNotifications = async () => {
  const resp = (await http.get('/b2-family/notifications', { params: notifyQuery })).data.data || {}
  notifications.value = resp.items || []
}

const loadBase = async () => {
  elders.value = (await http.get('/elders')).data.data
  await loadFamilies()
  await loadNotifications()
  serviceCatalog.value = (await http.get('/b2-family/services/catalog')).data.data
}

const loadElderPortalData = async () => {
  if (!selectedElderId.value) return
  elderOverview.value = (await http.get(`/b2-family/elders/${selectedElderId.value}/overview`)).data.data
  const billResp = (await http.get(`/b2-family/elders/${selectedElderId.value}/bills`, { params: billQuery })).data.data || {}
  bills.value = billResp.items || []
  billTotal.value = billResp.total || 0
  const recordResp = (await http.get(`/b2-family/elders/${selectedElderId.value}/care-records`, { params: recordQuery })).data.data || {}
  careRecords.value = recordResp.items || []
  surveys.value = ((await http.get('/b2-family/surveys', { params: { elder_id: selectedElderId.value, page: 1, page_size: 10 } })).data.data || {}).items || []
}

const createFamily = async () => {
  if (!form.elder_id || !form.name || !form.phone || !form.relation) return ElMessage.error('请完整填写家属信息')
  await http.post('/b2-family/accounts', form)
  form.name = ''; form.phone = ''; form.relation = ''
  ElMessage.success('家属账号创建成功')
  await loadFamilies()
}

const pickElderByFamily = async (row: any) => { selectedElderId.value = row.elder_id; await loadElderPortalData() }
const submitSurvey = async () => {
  if (!selectedElderId.value) return ElMessage.error('请先选择长者')
  await http.post('/b2-family/surveys', { elder_id: selectedElderId.value, score: survey.score, comment: survey.comment })
  survey.comment = ''
  ElMessage.success('评价提交成功')
  await loadElderPortalData(); await loadNotifications()
}
const placeServiceOrder = async () => {
  if (!selectedElderId.value || !serviceOrder.package_id) return ElMessage.error('请先选择长者和套餐')
  await http.post('/b2-family/services/order', { elder_id: selectedElderId.value, package_id: serviceOrder.package_id })
  ElMessage.success('增购下单成功')
  await loadElderPortalData(); await loadNotifications()
}

onMounted(loadBase)
</script>
