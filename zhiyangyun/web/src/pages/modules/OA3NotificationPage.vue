<template><ModuleCrudPage title="A2-OA3 通知" list-url="/oa3-notification/messages" create-url="/oa3-notification/messages" :fields="fields" :columns="columns" /></template>
<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'
const fields=[{key:'title',label:'title'},{key:'content',label:'content'},{key:'channel',label:'channel'},{key:'receiver_scope',label:'receiver_scope'}]
const columns=['id','title','channel','receiver_scope','sent_at']
</script>
