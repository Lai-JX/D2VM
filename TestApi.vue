<template>
  <h1>USER</h1>
  <el-form :inline="true" :model="registeryData" size="small">
    <el-form-item label="用户注册：" style="font-weight: bold;">
      <el-input
        class="input"
        v-model="registeryData.username"
        placeholder="用户名"
      ></el-input>
      <el-input
        class="input"
        v-model="registeryData.email"
        placeholder="email"
      ></el-input>
      <el-button type="primary" @click="onGetCode">获取验证码</el-button>
      <el-input
        class="input"
        v-model="registeryData.code"
        placeholder="验证码"
      ></el-input>
      <el-input
        class="input"
        v-model="registeryData.password"
        placeholder="password"
      ></el-input>
    </el-form-item>
    <el-form-item>
      <!-- <el-button type="primary" @click="onSubmitGet">get 查询所有</el-button> -->
      
      <el-button type="primary" @click="onRegister">post 注册</el-button>
    </el-form-item>
  </el-form>


  <el-form :inline="true" :model="changePwdData" size="small">
    <el-form-item label="修改密码" style="font-weight: bold;">
      <el-input
        class="input"
        v-model="changePwdData.username"
        placeholder="用户名"
      ></el-input>
      <el-input
        class="input"
        v-model="changePwdData.old_password"
        placeholder="old password"
      ></el-input>
      <el-input
        class="input"
        v-model="changePwdData.new_password"
        placeholder="new password"
      ></el-input>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="onChangePwd">修改密码</el-button>
    </el-form-item>
  </el-form>

  <el-form :inline="true" :model="resetPwdData" size="small">
    <el-form-item label="重置密码：" style="font-weight: bold;">
      <el-input
        class="input"
        v-model="resetPwdData.username"
        placeholder="用户名"
      ></el-input>
      <el-input
        class="input"
        v-model="resetPwdData.email"
        placeholder="email"
      ></el-input>
      <el-button type="primary" @click="onResetGetCode">获取验证码</el-button>
      <el-input
        class="input"
        v-model="resetPwdData.code"
        placeholder="验证码"
      ></el-input>
      <el-input
        class="input"
        v-model="resetPwdData.password"
        placeholder="password"
      ></el-input>
    </el-form-item>
    <el-form-item>
      <el-button type="primary" @click="onResetPwd">重置密码</el-button>
    </el-form-item>
  </el-form>

  <el-form :inline="true" :model="loginData" size="small">
    <el-form-item label="登录信息" style="font-weight: bold;">
      <el-input
        class="input"
        v-model="loginData.username"
        placeholder="用户名"
      ></el-input>
      <el-input
        class="input"
        v-model="loginData.password"
        placeholder="password"
      ></el-input>
    </el-form-item>
    <el-form-item>
      <!-- <el-button type="primary" @click="onSubmitGet">get 查询所有</el-button> -->
      <el-button type="primary" @click="onLogin">post 登录</el-button>
      <el-button type="primary" @click="onRegister">post 注册</el-button>
      <el-button type="primary" @click="onLogout">登出</el-button>
    </el-form-item>
  </el-form>
  
  <h1>CONTAINER</h1>
  <div>
    <form @submit.prevent="onCreateContainer" class="form">
      
      <div class="form-group">
        <label for="image">image_id:</label>
        <input type="text" v-model="containerData.image_id" required>
      </div>
      
      <div class="form-group">
        <label for="password">Password:</label>
        <input type="password" v-model="containerData.password" required>
      </div>
      
      <div class="form-group">
        <label for="cmd">Commands:</label>
        <input type="text" v-model="containerData.cmd">
      </div>
      
      <div class="form-group">
        <label for="path">Path:</label>
        <input type="text" v-model="containerData.path" required>
      </div>
      
      <div class="form-group">
        <label for="num_gpu">Number of vGPU:</label>
        <input type="number" v-model="containerData.num_gpu" required>
      </div>
      
      <div class="form-group">
        <label for="gpumem">Memory per vGPU (M):</label>
        <input type="number" v-model="containerData.gpumem" >
      </div>
      
      <div class="form-group">
        <label for="gpucores">Capacity of each vGPU (%):</label>
        <input type="number" v-model="containerData.gpucores" >
      </div>
      
      <div class="form-group">
        <label for="cpu">Number of CPU cores:</label>
        <input type="number" v-model="containerData.cpu" required>
      </div>
      
      
      <div class="form-group">
        <label for="duration">Duration of container(s):</label>
        <input type="number" v-model="containerData.duration" required>
      </div>
      
      <div class="form-group">
        <label for="memory">Memory size:</label>
        <input type="text" v-model="containerData.memory" required>
      </div>

      <div class="form-group">
        <label for="gputype">type of gpu:</label>
        <select id="gputype" v-model="containerData.gputype">
          <option value="">--</option>
          <option value="4090">NVIDIA GeForce RTX 4090</option>
          <option value="3090">NVIDIA GeForce RTX 3090</option>
          <option value="a6000">NVIDIA RTX A6000</option>
          <option value="h800">NVIDIA H800 PCIe</option>
        </select>
      </div>
      
      <div class="form-group">
        <!-- <label for="capability">Additional capability:</label>
        <input type="text" v-model="containerData.capability"> -->
        <div>
          <label>capability</label>
          <el-select v-model="selectedCapability" multiple placeholder="select additional capability">
            <el-option
              v-for="capability in capabilities"
              :key="capability"
              :value="capability"
            ></el-option>
          </el-select>
        </div>
      </div>

      <div class="form-group">
        <label for="shm">share memory:</label>
        <input type="test" v-model="containerData.shm">
      </div>

      <div class="form-group">
        <label for="hostname">hostname:</label>
        <input type="test" v-model="containerData.hostname">
      </div>

      <div class="form-group">
        <label for="ephemeral_storage">ephemeral_storage:</label>
        <input type="test" v-model="containerData.ephemeral_storage">
      </div>

      <div class="form-group">
        <label for="is_VM">Deploy VM(or Task):</label>
        <input type="checkbox" v-model="containerData.is_VM">
      </div>
      
      <div class="form-group">
        <label for="use_master">Deploy the VM in master node:</label>
        <input type="checkbox" v-model="containerData.use_master">
      </div>
      <button type="submit">Submit</button>
    </form>
  </div>

  <el-button type="primary" @click="onGetAllContainer">获取容器</el-button>
  <ul>
      <!-- 使用 v-for 遍历数组中的每个对象 -->
      <li v-for="(item, index) in container_results" :key="index">
        <!-- 显示对象中的属性 -->
        <p>pod_name: {{ item.pod_name }}</p>
        <p>image: {{ item.image_name }}</p>
        <p>ip: {{ item.node_ip }}</p>
        <p>port: {{ item.port }}</p>
        <p>create_time: {{ item.create_time }}</p>
        <p>duration: {{ item.duration }}</p>
        <p>status: {{ item.status }}</p>
      </li>
  </ul>

  <div>
    <el-input
      class="input"
      v-model="restart_container_id"
      placeholder="container_id"
    ></el-input>
    <button @click="onDockerRestart">Restart</button>
  </div>

  <div>
    <el-input
      class="input"
      v-model="delete_container_id"
      placeholder="container_id"
    ></el-input>
    <button @click="onDeleteContainer">Delete</button>
  </div>


  <h1>IMAGE</h1>
  <div>
    <form @submit.prevent="onAddImage">

      <label for="name">Name:</label>
      <input v-model="imageData.name" type="text" id="name" required>

      <label for="tag">Tag:</label>
      <input v-model="imageData.tag" type="text" id="tag">

      <label for="note">note:</label>
      <input v-model="imageData.note" type="text" id="note"  >

      <button type="submit">添加镜像</button>
    </form>
  </div>

  <div>
    <form @submit.prevent="onImageaddNote">

      <label for="image_id">image_id:</label>
      <input v-model="add_note_image_id" type="text" id="image_id" required>

      <label for="note">note:</label>
      <input v-model="image_add_note" type="text" id="note"  >

      <button type="submit">添加备注</button>
    </form>
  </div>

  <el-button type="primary" @click="onGetAllImage">获取镜像</el-button>
  <ul>
      <!-- 使用 v-for 遍历数组中的每个对象 -->
      <li v-for="(item, index) in image_results" :key="index">
        <!-- 显示对象中的属性 -->
        <p>image_id: {{ item.image_id }}</p>
        <p>name: {{ item.name }}</p>
        <p>tag: {{ item.tag }}</p>
        <p>source: {{ item.source }}</p>
        <p>note: {{ item.note }}</p>
        <p>record_datetime: {{ item.record_datetime }}</p>
        <p>is_push: {{ item.is_push }}</p>
      </li>
  </ul>

  <div>
    <el-input
      class="input"
      v-model="save_container_id"
      placeholder="container_id"
    ></el-input>
    <button @click="onSaveImage">Save</button>
  </div>

  <div>
    <el-input
      class="input"
      v-model="push_image_id"
      placeholder="image_id"
    ></el-input>
    <button @click="onPushImage">Push</button>
  </div>

  <div>
      <label for="delete_image_id">delete_image_id:</label>
      <input type="text" v-model="delete_image_id">


      <label for="delete_opt">delete_opt(0:delete_local; 1:delete_registry; 2:delete_all):</label>
      <input type="text" v-model="delete_opt">

    <button @click="onDeleteImage">Delete</button>
  </div>
  <div>
    <label for="chmod_image_id">chmod_image_id:</label>
    <input type="text" v-model="chmod_image_id">


    <label for="chmod_is_public">chmod_is_public(0:false; 1:true):</label>
    <input type="text" v-model="chmod_is_public">

  <button @click="onImageChmod">change</button>
</div>

<h1>NODE</h1>
<el-button type="primary" @click="onGetAllNode">get节点资源信息</el-button>
  <ul>
      <!-- 使用 v-for 遍历数组中的每个对象 -->
      <li v-for="(item, index) in node_results" :key="index">
        <!-- 显示对象中的属性 -->
        <p>node_id: {{ item.node_id }}</p>
        <p>节点名: {{ item.node_name }}</p>
        <p>gpu类型: {{ item.gputype }}</p>
        <p>gpu数量: {{ item.gpu_num }}</p>
        <p>剩余gpu数量: {{ item.gpu_remain_num }}</p>
      </li>
  </ul>



  <!-- <div>
    <button @click="onSyncImage">同步私有镜像库中的镜像数据到数据库（debug用）</button>
  </div> -->
  <h1>测试</h1>
  <el-form :inline="true" :model="registerDataPre" size="small">
    <el-form-item label="用户信息">
      <el-input
        class="input"
        v-model="registerDataPre.username"
        placeholder="用户名"
      ></el-input>
      <el-input
        class="input"
        v-model="registerDataPre.password"
        placeholder="password"
      ></el-input>
      <el-input
        class="input"
        v-model="registerDataPre.email"
        placeholder="email"
      ></el-input>
    </el-form-item>
    <el-form-item>
      <!-- <el-button type="primary" @click="onSubmitGet">get 查询所有</el-button> -->
      <!-- <el-button type="primary" @click="onLogin">post 登录</el-button> -->
      <el-button type="primary" @click="onRegisterPre">post 注册</el-button>
      <!-- <el-button type="primary" @click="onLogout">登出</el-button> -->
    </el-form-item>
  </el-form>
  <el-button type="primary" @click="onAsync">异步</el-button>
</template>

<script>
import axios from "axios";
// import Axios from 'axios'
// import {getBooks, postBook} from '../api/api.js'
let globalToken = ''
let username = ''
export default {
  props: {
    msg: String // 或其他类型
  },
  data() {
    return {
      loginData: {
        username: "",
        password: "",
      },
      registeryData: {
        username: "",
        email: "",
        code: "",
        password: "",
      },
      changePwdData: {
        username: "",
        old_password: "",
        new_password: "",
      },
      resetPwdData: {
        username: "",
        email: "",
        code: "",
        password: "",
      },
      registerDataPre: {
        username: "",
        email: "",
        password: "",
      },
      containerData: {
        name: 'myubuntu',
        image_id: 3,
        password: '123456',
        cmd: '',
        path: '/workspace',
        num_gpu: 1,
        gpumem: '',
        gpucores: '',
        cpu: 1,
        // port: null,
        duration: 3600,
        memory: '1Gi',
        capabilities: null,
        is_VM: true,
        use_master: false,
        gputype: '',
        shm: '64M',
        hostname: '',
        ephemeral_storage: '',
      },
      capabilities: ['CAP_SYS_ADMIN', 'NET_BIND_SERVICE'],
      selectedCapability: null,
      imageData: {
        name: '',
        tag: '',
        source: '',
        note: '',
      },
      container_results: "",
      image_results: "",
      node_results: "",
      delete_container_id: "",
      save_container_id: "",
      push_image_id: "",
      delete_image_id: "",
      delete_opt: "",
      image_add_note: "",
      add_note_image_id: "",
      restart_container_id: "",
      chmod_image_id: "",
      chmod_is_public: "",
    };
  },
  methods: {
    onLogin() {
      console.log("onLogin!");
      console.log("data",this.loginData)
      axios.post("http://10.249.40.11:32325/user/login/", this.loginData)
      .then((res) => {
         console.log('success')
         console.log(res.data, this.loginData.username); //在console中看到数据
         globalToken = res.data.token
         username = this.loginData.username
        })
        .catch((res) => {
          alert("wrong",res.data);
        });
    },

    onGetCode() {
      console.log("onGetCode!");

      var getCodeData = {getCodeData:'', email:''}
      getCodeData.username=this.registeryData.username
      getCodeData.email=this.registeryData.email

      axios.post("http://10.249.40.11:32325/user/register/sendCode/", getCodeData)
      .then((res) => {
         console.log('success')
         console.log(res); //在console中看到数据
        })
        .catch((res) => {
          console.log(res)
          if (res.response.status==400) {
            alert("wrong:"+JSON.stringify(res.response.data));
          }
            
        });
    },
    
    onRegister() {
      console.log("onRegister!");
      console.log("data",this.registeryData)
      axios.post("http://10.249.40.11:32325/user/register/", this.registeryData)
      .then((res) => {
         console.log('success')
         console.log(res); //在console中看到数据
        })
        .catch((res) => {
          console.log(res); //在console中看到数据
          if (res.response.status==400) {
            alert("wrong:"+JSON.stringify(res.response.data));
          }
        });
    },

    onChangePwd() {
      console.log("onChangePwd!");
      console.log("data",this.changePwdData)
      axios.patch("http://10.249.40.11:32325/user/changePwd/", this.changePwdData, {
        headers: {
          Authorization: `Token ${globalToken}`,
        },
      })
      .then((res) => {
         console.log('success')
         console.log(res); //在console中看到数据
        })
        .catch((res) => {
          console.log(res); //在console中看到数据
        });
    },

    onResetGetCode() {
      console.log("onResetGetCode!");

      var getCodeData = {getCodeData:'', email:''}
      getCodeData.username=this.resetPwdData.username
      getCodeData.email=this.resetPwdData.email

      axios.post("http://10.249.40.11:32325/user/reset/sendCode/", getCodeData)
      .then((res) => {
         console.log('success')
         console.log(res); //在console中看到数据
        })
        .catch((res) => {
          console.log(res)
          if (res.response.status==400) {
            alert("wrong:"+JSON.stringify(res.response.data));
          }
            
        });
    },
    
    onResetPwd() {
      console.log("onResetPwd!");
      console.log("data",this.resetPwdData)
      axios.post("http://10.249.40.11:32325/user/reset/", this.resetPwdData)
      .then((res) => {
         console.log('success')
         console.log(res); //在console中看到数据
        })
        .catch((res) => {
          console.log(res); //在console中看到数据
          if (res.response.status==400) {
            alert("wrong:"+JSON.stringify(res.response.data));
          }
        });
    },

    onRegisterPre() {
      console.log("onRegisterPre!");
      console.log("data",this.registerDataPre)
      axios.post("http://10.249.40.11:32325/user/register_test/", this.registerDataPre)
      .then((res) => {
         console.log('success')
         console.log(res); //在console中看到数据
        })
        .catch((res) => {
          console.log(res); //在console中看到数据
          if (res.response.status==400) {
            alert("wrong:"+JSON.stringify(res.response.data));
          }
        });
    },

    onLogout() {
      console.log("onLogout!");
      axios.get('http://10.249.40.11:32325/user/logout/', {
        headers: {
          Authorization: `Token ${globalToken}`,
        },
      })
      .then((res) => {
         console.log('success')
         console.log(res.data); //在console中看到数据
        })
        .catch((res) => {
          alert("wrong",res.data);
        });
    },

    onCreateContainer() {
      console.log("onCreateContainer!");
      this.containerData.name = username
      this.containerData.capabilities = this.selectedCapability
      this.containerData = Object.fromEntries(
        Object.entries(this.containerData).filter(([, value]) => value !== null && value !== "")
      );
      console.log("data",this.containerData)
      axios.post("http://10.249.40.11:32325/container/", this.containerData, {
        headers: {
          Authorization: `Token ${globalToken}`,
        },
      })
      .then((res) => {
         console.log('success')
         console.log(res.data); //在console中看到数据
        })
        .catch((res) => {
          alert("wrong",res.data);
        });
    },

    onGetAllContainer() {
      console.log("onGetAllContainer!");
      axios.get('http://10.249.40.11:32325/container/get/', {
        headers: {
          Authorization: `Token ${globalToken}`,
        },
      })
      .then((res) => {
         console.log('success')
         console.log(res.data); //在console中看到数据
         this.container_results = res.data
        })
        .catch((res) => {
          alert("wrong",res.data);
        });
    },

    onDeleteContainer() {
      console.log("onDeleteContainer!", this.delete_container_id);
      axios.delete('http://10.249.40.11:32325/container/?container_id='+this.delete_container_id, {
        headers: {
          Authorization: `Token ${globalToken}`,
        },
      })
      .then((res) => {
         console.log(res.data); //在console中看到数据
         this.container_results = res.data
        })
        .catch((res) => {
          alert("wrong",res.data);
        });
    },

    onDockerRestart() {
      console.log('onDockerRestart')
      console.log(this.restart_container_id)
      // 发起 get 请求
      axios.get('http://10.249.40.11:32325/container/dockerRestart/', {
          headers: {
            Authorization: `Token ${globalToken}`,
          },
          params: {
            container_id: this.restart_container_id,
          },
        })
        .then(response => {
          console.log('request successful', response.data);
          // 处理响应数据
        })
        .catch(error => {
          console.error('Error making request', error);
          // 处理错误
        });
    },


    onAddImage() {
      console.log("onAddImage!");
      console.log("data",this.imageData)
      // 例如，您可以在这里使用 Axios 或 Fetch 发送数据到后端
      axios.post("http://10.249.40.11:32325/image/", this.imageData, {
        headers: {
          Authorization: `Token ${globalToken}`,
        },
      })
      .then((res) => {
         console.log('success')
         console.log(res.data); //在console中看到数据
        })
        .catch((res) => {
          alert("wrong",res.data);
        });
    },

    onGetAllImage() {
      console.log("onGetAllImage!");
      axios.get('http://10.249.40.11:32325/image/', {
        headers: {
          Authorization: `Token ${globalToken}`,
        },
      })
      .then((res) => {
         console.log('success')
         console.log(res.data); //在console中看到数据
        //  this.image_results = [res.data]
         this.image_results = res.data
        })
        .catch((res) => {
          alert("wrong",res.data);
        });
    },

    onSaveImage() {
      // console.log('onSaveImage')
      console.log("onSaveImage!", this.save_container_id);
      // 发起 PATCH 请求
      axios.get('http://10.249.40.11:32325/image/save/?container_id=' + this.save_container_id, {
          headers: {
            Authorization: `Token ${globalToken}`,
          },
        })
        .then(response => {
          console.log('SaveImage request successful', response.data);
          // 处理响应数据
        })
        .catch(error => {
          console.error('Error making SaveImage request', error);
          // 处理错误
        });
    },

    onPushImage() {
      console.log("onPushImage!", this.push_image_id);
      // 发起 PATCH 请求
      axios.get('http://10.249.40.11:32325/image/push/?image_id=' + this.push_image_id, {
          headers: {
            Authorization: `Token ${globalToken}`,
          },
        })
        .then(response => {
          console.log('PushImage request successful', response.data);
          // 处理响应数据
        })
        .catch(error => {
          console.error('Error making PushImage request', error);
          // 处理错误
        });
    },

    onDeleteImage() {
      console.log("onDeleteImage!", this.delete_image_id, this.delete_opt);
      axios.delete('http://10.249.40.11:32325/image/', {
        headers: {
          Authorization: `Token ${globalToken}`,
        },
        params: {
          image_id: this.delete_image_id,
          delete_opt: this.delete_opt,
        },
      })
      .then((res) => {
         console.log(res.data); //在console中看到数据
         this.container_results = res.data
        })
        .catch((res) => {
          alert("wrong",res.data);
        });
    },

    onImageaddNote() {
      console.log('onImageaddNote')
      console.log(this.add_note_image_id, this.image_add_note, globalToken)
      // 发起 get 请求
      axios.get('http://10.249.40.11:32325/image/addNote/', {
          headers: {
            Authorization: `Token ${globalToken}`,
          },
          params: {
            image_id: this.add_note_image_id,
            note: this.image_add_note,
          },
        })
        .then(response => {
          console.log('request successful', response.data);
          // 处理响应数据
        })
        .catch(error => {
          console.error('Error making request', error);
          // 处理错误
        });
    },

    onImageChmod() {
      console.log('onImageChmod')
      // 发起 get 请求
      axios.get('http://10.249.40.11:32325/image/chmod/', {
          headers: {
            Authorization: `Token ${globalToken}`,
          },
          params: {
            image_id: this.chmod_image_id,
            is_public: this.chmod_is_public,      // 0:false; 1:true
          },
        })
        .then(response => {
          console.log('request successful', response.data);
          // 处理响应数据
        })
        .catch(error => {
          console.error('Error making request', error);
          // 处理错误
        });
    },

    onGetAllNode() {
      console.log("onGetAllNode!");
      axios.get('http://10.249.40.11:32325/node/', {
        headers: {
          Authorization: `Token ${globalToken}`,
        },
      })
      .then((res) => {
         console.log('success')
         console.log(res.data); //在console中看到数据
         this.node_results = res.data
        })
        .catch((res) => {
          alert("wrong",res.data);
        });
    },


    onAsync() {
      axios.get('http://10.249.40.11:32325/image/test/', {})
        .then(response => {
          console.log('request successful', response.data);
          // 处理响应数据
        })
        .catch(error => {
          console.error('Error making request', error);
          // 处理错误
        });
    }

    // onSyncImage() {
    //   // 发起 PATCH 请求
    //   axios.patch('http://10.249.40.11:32325/image/sync/', {}, {
    //       headers: {
    //         Authorization: `Token ${globalToken}`,
    //       },
    //     })
    //     .then(response => {
    //       console.log('PATCH request successful', response.data);
    //       // 处理响应数据
    //     })
    //     .catch(error => {
    //       console.error('Error making PATCH request', error);
    //       // 处理错误
    //     });
    // }

  },
};
</script>

<style scoped>
.input {
  width: 200px;
}
button {
  width: 100px;
}
.textarea {
  width: 900px;
}

.form {
  display: flex;
  flex-wrap: wrap;
}

.form-group {
  width: 50%;
  box-sizing: border-box;
  margin-bottom: 10px;
}
</style>