<template>
  <h1>USER</h1>
  <el-form :inline="true" :model="formInline" size="small">
    <el-form-item label="用户信息">
      <el-input
        class="input"
        v-model="formInline.username"
        placeholder="用户名"
      ></el-input>
      <el-input
        class="input"
        v-model="formInline.password"
        placeholder="password"
      ></el-input>
      <el-input
        class="input"
        v-model="formInline.email"
        placeholder="email"
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
          <option value="a6000">NVIDIA RTX A6000</option>
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
      <input v-model="imageData.tag" type="text" id="tag" required>

      <label for="note">note:</label>
      <input v-model="imageData.note" type="text" id="note"  >

      <button type="submit">添加镜像</button>
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


      <label for="delete_image_all">delete_image_all(delet the image in registry):</label>
      <input type="checkbox" v-model="delete_image_all">

    <button @click="onDeleteImage">Delete</button>
  </div>

  <!-- <div>
    <button @click="onSyncImage">同步私有镜像库中的镜像数据到数据库（debug用）</button>
  </div> -->

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
      formInline: {
        username: "",
        password: "",
        email: "",
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
        shm: '64M'
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
      delete_container_id: "",
      save_container_id: "",
      push_image_id: "",
      delete_image_id: "",
      delete_image_all: false,
    };
  },
  methods: {
    onLogin() {
      console.log("onLogin!");
      console.log("data",this.formInline)
      axios.post("http://10.249.46.117:32325/user/login/", this.formInline)
      .then((res) => {
         console.log('success')
         console.log(res.data, this.formInline.username); //在console中看到数据
         globalToken = res.data.token
         username = this.formInline.username
        })
        .catch((res) => {
          alert("wrong",res.data);
        });
    },
    
    onRegister() {
      console.log("onRegister!");
      console.log("data",this.formInline)
      axios.post("http://10.249.46.117:32325/user/register/", this.formInline)
      .then((res) => {
         console.log('success')
         console.log(res.data); //在console中看到数据
        })
        .catch((res) => {
          alert("wrong",res.data);
        });
    },

    onLogout() {
      console.log("onLogout!");
      axios.get('http://10.249.46.117:32325/user/logout/', {
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
      axios.post("http://10.249.46.117:32325/container/", this.containerData, {
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
      axios.get('http://10.249.46.117:32325/container/get/', {
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
      axios.delete('http://10.249.46.117:32325/container/?container_id='+this.delete_container_id, {
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


    onAddImage() {
      console.log("onAddImage!");
      console.log("data",this.imageData)
      // 例如，您可以在这里使用 Axios 或 Fetch 发送数据到后端
      axios.post("http://10.249.46.117:32325/image/", this.imageData, {
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
      axios.get('http://10.249.46.117:32325/image/', {
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
      axios.get('http://10.249.46.117:32325/image/save/?container_id=' + this.save_container_id, {
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
      axios.get('http://10.249.46.117:32325/image/push/?image_id=' + this.push_image_id, {
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
      console.log("onDeleteImage!", this.delete_image_id, this.delete_image_all);
      axios.delete('http://10.249.46.117:32325/image/', {
        headers: {
          Authorization: `Token ${globalToken}`,
        },
        params: {
          image_id: this.delete_image_id,
          delete_all: this.delete_image_all ? 1 : '',
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

    // onSyncImage() {
    //   // 发起 PATCH 请求
    //   axios.patch('http://10.249.46.117:32325/image/sync/', {}, {
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