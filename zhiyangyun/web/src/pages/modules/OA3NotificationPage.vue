<template>
  <ModuleCrudPage
    title="A2-OA3 通知公告"
    description="支持公告通知、系统消息。"
    list-url="/oa3-notification/messages"
    create-url="/oa3-notification/messages"
    :fields="fields"
    :columns="columns"
  />
</template>

<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'

const fields = [
  { key: 'title', label: '标题', required: true },
  { key: 'content', label: '内容', type: 'textarea', required: true },
  {
    key: 'channel',
    label: '消息渠道',
    type: 'select',
    required: true,
    options: [
      { label: '系统内', value: 'system' },
      { label: '短信', value: 'sms' },
      { label: '邮件', value: 'email' }
    ]
  },
  {
    key: 'receiver_scope',
    label: '接收范围',
    type: 'select',
    required: true,
    options: [
      { label: '全员', value: 'all' },
      { label: '护理员', value: 'caregiver' },
      { label: '医护', value: 'medical' }
    ]
  }
]

const columns = [
  { prop: 'id', label: 'ID' },
  { prop: 'title', label: '标题' },
  { prop: 'channel', label: '渠道' },
  { prop: 'receiver_scope', label: '接收范围' },
  { prop: 'sent_at', label: '发送时间' }
]
</script>
