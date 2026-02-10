<template><ModuleCrudPage title="A2-OA2 审批" list-url="/oa2-approval/requests" create-url="/oa2-approval/requests" :fields="fields" :columns="columns" /></template>
<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'
const fields=[{key:'module',label:'module'},{key:'biz_id',label:'biz_id'},{key:'applicant_id',label:'applicant_id'},{key:'approver_id',label:'approver_id'}]
const columns=['id','module','biz_id','applicant_id','approver_id','status']
</script>
