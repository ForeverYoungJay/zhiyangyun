<template>
  <div class="page-shell">
    <div class="page-title">
      <div>
        <h2>B2 家属门户闭环</h2>
        <div class="desc">打通家属账号、账单、护理记录与评价反馈，形成服务-财务-满意度联动。</div>
      </div>
    </div>

    <el-row :gutter="16">
      <el-col :span="8">
        <el-card class="zy-card">
          <template #header>
            <div>
              <div>家属账号</div>
              <div style="font-size:12px;color:#909399">先绑定长者，再填写家属信息。</div>
            </div>
          </template>
          <el-form label-width="90px">
            <el-form-item label="关联长者">
              <el-select v-model="form.elder_id" placeholder="请选择长者" style="width:100%">
                <el-option v-for="e in elders" :key="e.id" :label="e.name" :value="e.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="家属姓名"><el-input v-model="form.name" placeholder="例如：王小明" /></el-form-item>
            <el-form-item label="手机号"><el-input v-model="form.phone" placeholder="11位手机号" /></el-form-item>
            <el-form-item label="关系">
              <el-select v-model="form.relation" placeholder="请选择关系" style="width:100%">
                <el-option label="子女" value="子女" />
                <el-option label="配偶" value="配偶" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
            <el-button type="primary" @click="createFamily">新增家属</el-button>
          </el-form>
          <el-table :data="families" style="margin-top:10px" @row-click="pickElderByFamily" border>
            <el-table-column prop="name" label="家属"/>
            <el-table-column prop="relation" label="关系"/>
            <el-table-column prop="elder_id" label="长者ID"/>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card class="zy-card">
          <template #header>
            <div>
              <div>家属可见账单 / 护理记录 / 问卷评价</div>
              <div style="font-size:12px;color:#909399">请先在下方选择一个长者。</div>
            </div>
          </template>
          <div style="margin-bottom:10px">
            <el-select v-model="selectedElderId" placeholder="选择长者" style="width:260px" @change="loadElderPortalData">
              <el-option v-for="e in elders" :key="e.id" :label="e.name" :value="e.id" />
            </el-select>
          </div>

          <el-tabs>
            <el-tab-pane label="账单明细">
              <el-table :data="bills" border>
                <el-table-column prop="item_name" label="项目"/>
                <el-table-column prop="amount" label="金额"/>
                <el-table-column prop="charged_on" label="扣费日期"/>
                <el-table-column prop="status" label="状态">
                  <template #default="scope"><el-tag :class="statusTagClass(scope.row.status)">{{ scope.row.status }}</el-tag></template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="护理记录">
              <el-table :data="careRecords" border>
                <el-table-column prop="content" label="内容"/>
                <el-table-column prop="occurred_at" label="时间"/>
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="问卷评价">
              <el-form inline>
                <el-form-item label="评分"><el-rate v-model="survey.score" /></el-form-item>
                <el-form-item>
                  <el-input v-model="survey.comment" placeholder="请填写本次服务评价" style="width:320px"/>
                </el-form-item>
                <el-button type="primary" @click="submitSurvey">提交</el-button>
              </el-form>
              <el-table :data="surveys" border style="margin-top:10px">
                <el-table-column prop="score" label="评分"/>
                <el-table-column prop="comment" label="评价"/>
                <el-table-column prop="created_at" label="时间"/>
              </el-table>
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
const bills = ref<any[]>([])
const careRecords = ref<any[]>([])
const surveys = ref<any[]>([])
const selectedElderId = ref('')

const form = reactive({ elder_id: '', name: '', phone: '', relation: '' })
const survey = reactive({ score: 5, comment: '' })

const loadBase = async () => {
  elders.value = (await http.get('/elders')).data.data
  families.value = (await http.get('/b2-family/accounts')).data.data
}

const loadElderPortalData = async () => {
  if (!selectedElderId.value) return
  bills.value = (await http.get(`/b2-family/elders/${selectedElderId.value}/bills`)).data.data
  careRecords.value = (await http.get(`/b2-family/elders/${selectedElderId.value}/care-records`)).data.data
  surveys.value = (await http.get('/b2-family/surveys', { params: { elder_id: selectedElderId.value } })).data.data
}

const createFamily = async () => {
  if (!form.elder_id || !form.name || !form.phone || !form.relation) return ElMessage.error('请完整填写家属信息')
  await http.post('/b2-family/accounts', form)
  form.name = ''
  form.phone = ''
  form.relation = ''
  ElMessage.success('家属账号创建成功')
  await loadBase()
}

const pickElderByFamily = async (row: any) => {
  selectedElderId.value = row.elder_id
  await loadElderPortalData()
}

const submitSurvey = async () => {
  if (!selectedElderId.value) return ElMessage.error('请先选择长者')
  await http.post('/b2-family/surveys', { elder_id: selectedElderId.value, score: survey.score, comment: survey.comment })
  survey.comment = ''
  ElMessage.success('评价提交成功')
  await loadElderPortalData()
}

const statusTagClass = (status: string) => {
  if (status === 'paid' || status === 'completed') return 'zy-tag-success'
  if (status === 'pending') return 'zy-tag-warning'
  return 'zy-tag-info'
}

onMounted(loadBase)
</script>
