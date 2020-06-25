var app = new Vue({
  el: '#app',
  created: function () {
    this.getLoggedEntity();
  },
  data: {
    loginData: { cpf_cnpj: '71484654862', password: '123change' },
    signUpData: { name: 'Loja do Ze', cpf_cnpj: '34792144697825', password: '123change' },
    chargeData: {
      "debtor": {
        "name": "Loja do Ze",
        "cpf_cnpj": "34792144697825"
      },
      "creditor_cpf_cnpj": '71484654862',
      "debito": 1000.26
    },
    chargesList: [],
    loggedUser: { name: '', cpf_cnpj: '' },
    search: '34792144697825',
    showLogin: true,
    isLoading: false,

    // Errors:
    errorLogin: '',
    errorSignUp: '',
    errorCharge: '',
  },
  methods: {
    getLoggedEntity: function () {
      return axios.get('/api/v.1/entity-logged')
        .then((response) => {
          this.loggedUser.cpf_cnpj = response.data.cpf_cnpj;
          this.loggedUser.name = response.data.name;
          this.showLogin = false;
        })
        .catch((error) => {
          if (error.response.status === 422) {
            this.errorLogin = error.response.data.detail[0].msg;
            return;
          }
          if (error.response.status === 400) {
            this.errorLogin = error.response.data.detail;
            return;
          }
          console.log(error.response.data);
        });
    },
    doLogin: function (loginData) {
      const { cpf_cnpj, password } = loginData;
      return axios.post('/api/v.1/authenticate', {
        cpf_cnpj: cpf_cnpj,
        password: password,
        set_cookie: true,
      })
        .then((response) => {
          this.loggedUser.cpf_cnpj = response.data.cpf_cnpj;
          this.showLogin = false;
        })
        .catch((error) => {
          if (error.response.status === 422) {
            this.errorLogin = error.response.data.detail[0].msg;
            return;
          }
          if (error.response.status === 400) {
            this.errorLogin = error.response.data.detail;
            return;
          }
          console.log(error.response.data);
        });
    },

    doLogout: function () {
      axios.delete('/api/v.1/authenticate')
        .then((response) => {
          this.showLogin = true;
          console.log(response);
        })
        .catch((error) => {
          console.log(error);
        });
    },

    doSignUp: function () {
      const { name, cpf_cnpj, password } = this.signUpData;
      return axios.post('/api/v.1/entity', {
        name: name,
        cpf_cnpj: cpf_cnpj,
        password: password,
      })
        .then((response) => {
          this.doLogin({
            cpf_cnpj: cpf_cnpj,
            password: password,
          });
        })
        .catch((error) => {
          if (error.response.status === 422) {
            this.errorSignUp = error.response.data.detail[0].msg;
            return;
          }
          if (error.response.status === 400) {
            this.errorSignUp = error.response.data.detail;
            return;
          }
          console.log(error);
        });
    },

    getCharges: function (search) {
      const params = {
        debtor_cpf_cnpj: search,
        is_active: true,
      }
      axios.get('/api/v.1/charge', { params: params })
        .then((response) => {
          this.chargesList = response.data.map(
            row => ({
              created_at: moment(row.created_at).format('L'),
              creditor_cpf_cnpj: row.creditor_cpf_cnpj,
              debito: row.debito,
              debtor_cpf_cnpj: row.debtor_cpf_cnpj,
              id: row.id,
              is_active: row.is_active,
              payed_at: row.payed_at,
            })
          );
        })
        .catch((error) => {
          if ([404, 422].indexOf(error.response.status) >= 0) {
            this.chargesList = [];
            this.errorCharge = "Pendência Não Encontrada"
            return;
          }
          console.log(error.response.data);
        });
    },

    createCharge: function (chargeData) {
      axios.post('/api/v.1/charge', chargeData)
        .then((response) => {
          this.getCharges(this.search);
          console.log(response)
        })
        .catch((error) => {
          if (error.response.status === 422) {
            console.log(error.response.data.detail[0].msg);
            return;
          }
          if (error.response.status === 400) {
            console.log(error.response.data.detail);
            return;
          }
          console.log(error.response.data);
        });
    },

    doPayment: function (paymentData) {
      axios.post('/api/v.1/charge/payment', paymentData)
        .then((response) => {
          this.getCharges(this.search);
          console.log(response);
        })
        .catch((error) => {
          console.log(error);
        });
    }
  }
})