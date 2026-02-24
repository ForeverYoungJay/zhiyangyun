<template>
  <div class="page-shell">
    <div class="page-title"><h2>A2-OA4 培训闭环</h2></div>
    <el-card class="zy-card">
      <template #header><div style="display:flex;justify-content:space-between"><span>培训计划</span><el-button type="primary" @click="courseVisible=true">新建计划</el-button></div></template>
      <el-form inline>
        <el-form-item label="关键字"><el-input v-model="courseQuery.keyword" clearable /></el-form-item>
        <el-form-item label="状态"><el-select v-model="courseQuery.status" clearable style="width:120px"><el-option label="计划中" value="planned" /><el-option label="已完成" value="completed"/></el-select></el-form-item>
        <el-button type="primary" @click="loadCourses">查询</el-button>
      </el-form>
      <el-table :data="courses.items" border>
        <el-table-column prop="title" label="课程" min-width="160"/>
        <el-table-column prop="trainer_name" label="讲师" width="120"/>
        <el-table-column prop="start_date" label="开始" width="110"/>
        <el-table-column prop="end_date" label="结束" width="110"/>
        <el-table-column prop="required_score" label="及格分" width="90"/>
        <el-table-column label="闭环"><template #default="{row}"><el-button link @click="showClosure(row.id)">查看</el-button></template></el-table-column>
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:12px"><el-pagination v-model:current-page="courseQuery.page" v-model:page-size="courseQuery.page_size" :total="courses.total" :page-sizes="[10,20,50]" layout="total, sizes, prev, pager, next" @change="loadCourses"/></div>
    </el-card>

    <el-card class="zy-card" style="margin-top:12px">
      <template #header><div style="display:flex;justify-content:space-between"><span>签到/考核</span><el-button @click="recordVisible=true">添加学员</el-button></div></template>
      <el-form inline>
        <el-form-item label="关键字"><el-input v-model="recordQuery.keyword" clearable /></el-form-item>
        <el-form-item label="状态"><el-select v-model="recordQuery.status" clearable style="width:120px"><el-option label="学习中" value="learning"/><el-option label="通过" value="completed"/><el-option label="未通过" value="failed"/></el-select></el-form-item>
        <el-button type="primary" @click="loadRecords">查询</el-button>
      </el-form>
      <el-table :data="records.items" border>
        <el-table-column prop="course_title" label="课程" min-width="140"/>
        <el-table-column prop="user_name" label="学员" width="120"/>
        <el-table-column prop="attendance_status" label="签到" width="90"/>
        <el-table-column prop="score" label="分数" width="80"/>
        <el-table-column prop="exam_status" label="考核" width="90"/>
        <el-table-column prop="status" label="闭环" width="90"/>
        <el-table-column label="操作" width="220"><template #default="{row}"><el-button link type="primary" @click="actRecord(row.id,'sign_in')">签到</el-button><el-button link type="danger" @click="actRecord(row.id,'absent')">缺勤</el-button><el-button link type="success" @click="assess(row.id)">考核</el-button></template></el-table-column>
      </el-table>
      <div style="display:flex;justify-content:flex-end;margin-top:12px"><el-pagination v-model:current-page="recordQuery.page" v-model:page-size="recordQuery.page_size" :total="records.total" :page-sizes="[10,20,50]" layout="total, sizes, prev, pager, next" @change="loadRecords"/></div>
    </el-card>

    <el-dialog v-model="courseVisible" title="新建培训计划" width="560px"><el-form :model="courseForm" label-width="90px"><el-form-item label="课程"><el-input v-model="courseForm.title"/></el-form-item><el-form-item label="类型"><el-input v-model="courseForm.category"/></el-form-item><el-form-item label="讲师"><el-select v-model="courseForm.trainer_id" filterable><el-option v-for="u in users" :key="u.id" :label="u.display_name" :value="u.id"/></el-select></el-form-item><el-form-item label="开始"><el-date-picker v-model="courseForm.start_date" value-format="YYYY-MM-DD"/></el-form-item><el-form-item label="结束"><el-date-picker v-model="courseForm.end_date" value-format="YYYY-MM-DD"/></el-form-item><el-form-item label="及格分"><el-input-number v-model="courseForm.required_score" :min="0" :max="100"/></el-form-item></el-form><template #footer><el-button @click="courseVisible=false">取消</el-button><el-button type="primary" @click="createCourse">提交</el-button></template></el-dialog>
    <el-dialog v-model="recordVisible" title="添加学员" width="520px"><el-form :model="recordForm" label-width="90px"><el-form-item label="课程"><el-select v-model="recordForm.course_id"><el-option v-for="c in courses.items" :key="c.id" :label="c.title" :value="c.id"/></el-select></el-form-item><el-form-item label="学员"><el-select v-model="recordForm.user_id" filterable><el-option v-for="u in users" :key="u.id" :label="u.display_name" :value="u.id"/></el-select></el-form-item></el-form><template #footer><el-button @click="recordVisible=false">取消</el-button><el-button type="primary" @click="createRecord">提交</el-button></template></el-dialog>

    <el-dialog v-model="closureVisible" title="闭环统计" width="420px"><div>总人数：{{ closure.total }}；签到：{{ closure.signed_in }}；通过：{{ closure.passed }}；闭环：{{ closure.closed_loop }}；闭环率：{{ closure.closure_rate }}%</div></el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../../api/http'

const users = ref<any[]>([])
const courses = reactive<any>({ items: [], total: 0 })
const records = reactive<any>({ items: [], total: 0 })
const courseQuery = reactive({ page: 1, page_size: 10, keyword: '', status: '' })
const recordQuery = reactive({ page: 1, page_size: 10, keyword: '', status: '' })

const courseVisible = ref(false)
const recordVisible = ref(false)
const closureVisible = ref(false)
const closure = reactive<any>({})
const courseForm = reactive<any>({ title: '', category: 'care', trainer_id: '', start_date: '', end_date: '', required_score: 60 })
const recordForm = reactive<any>({ course_id: '', user_id: '' })

const loadUsers = async () => { users.value = (await http.get('/oa4-training/users/suggest')).data.data || [] }
const loadCourses = async () => { Object.assign(courses, (await http.get('/oa4-training/courses', { params: courseQuery })).data.data || { items: [], total: 0 }) }
const loadRecords = async () => { Object.assign(records, (await http.get('/oa4-training/records', { params: recordQuery })).data.data || { items: [], total: 0 }) }
const createCourse = async () => { await http.post('/oa4-training/courses', courseForm); ElMessage.success('计划已创建'); courseVisible.value = false; loadCourses() }
const createRecord = async () => { await http.post('/oa4-training/records', recordForm); ElMessage.success('学员已加入'); recordVisible.value = false; loadRecords() }
const actRecord = async (id: string, action: string) => { await http.post(`/oa4-training/records/${id}/action`, { action }); ElMessage.success('已更新'); loadRecords() }
const assess = async (id: string) => { const prompt: any = await ElMessageBox.prompt('请输入考核分数', '考核', { inputPattern: /^(100|[1-9]?\d)$/, inputErrorMessage: '0-100' }); await http.post(`/oa4-training/records/${id}/action`, { action: 'assess', score: Number(prompt.value) }); ElMessage.success('考核完成'); loadRecords() }
const showClosure = async (courseId: string) => { Object.assign(closure, (await http.get(`/oa4-training/courses/${courseId}/closure`)).data.data || {}); closureVisible.value = true }

onMounted(async () => { await loadUsers(); await loadCourses(); await loadRecords() })
</script>