<template>
  <div style="display:flex;height:100vh;">
    <el-menu router default-active="/assets/overview" style="width:220px;">
      <el-menu-item index="/assets/overview">资产总览</el-menu-item>
      <el-menu-item index="/assets/buildings">楼栋管理</el-menu-item>
      <el-menu-item index="/assets/floors">楼层管理</el-menu-item>
      <el-menu-item index="/assets/rooms">房间管理</el-menu-item>
      <el-menu-item index="/assets/beds">床位管理</el-menu-item>
      <el-menu-item index="/assets/qrcodes">二维码管理</el-menu-item>
    </el-menu>
    <div style="flex:1;overflow:auto;">
      <div style="height:56px;border-bottom:1px solid #eee;display:flex;align-items:center;justify-content:space-between;padding:0 16px;">
        <div>智慧养老平台 - 资产管理 M1</div>
      </div>
      <div style="padding:16px;"><router-view /></div>
    </div>
  </div>
</template>
