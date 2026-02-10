<template><ModuleCrudPage title="B2 家属门户" list-url="/b2-family/accounts" create-url="/b2-family/accounts" :fields="fields" :columns="columns" /></template>
<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'
const fields=[{key:'elder_id',label:'elder_id'},{key:'name',label:'name'},{key:'phone',label:'phone'},{key:'relation',label:'relation'}]
const columns=['id','elder_id','name','phone','relation']
</script>
