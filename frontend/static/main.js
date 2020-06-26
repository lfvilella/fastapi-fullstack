var app = new Vue({
  el: '#app',
  created: function () {
    this.getLoggedEntity();
    this.getHomePage();
  },
  data: {
    loginData: { cpf_cnpj: '', password: '' },
    signUpData: { name: '', cpf_cnpj: '', password: '' },
    chargeData: {
      "debtor": {
        "name": "",
        "cpf_cnpj": ""
      },
      "creditor_cpf_cnpj": "",
      "debito": 0
    },
    chargesList: [],
    loggedUser: { name: '', cpf_cnpj: '' },
    search: '',
    showLogin: true,
    isLoading: true,
    isLoadingCharge: false,

    // Errors:
    errorLogin: '',
    errorSignUp: '',
    errorCharge: '',
    errorCreateCharge: '',
  },
  methods: {
    cleanAllMensagens: function () {
      this.errorLogin = '';
      this.errorSignUp = '';
      this.errorCharge = '';
      this.errorCreateCharge = '';
      this.loginData = { cpf_cnpj: '', password: '' };
      this.signUpData = { name: '', cpf_cnpj: '', password: '' };
      this.chargeData = {
        "debtor": {
          "name": "",
          "cpf_cnpj": ""
        },
        "creditor_cpf_cnpj": "",
        "debito": 0
      };
      return;
    },

    setLoadingState: function (value) {
      return this.isLoading = value;
    },

    getHomePage: function () {
      return axios.get('/')
        .then((response) => {
          this.isLoading = false;
          this.cleanAllMensagens();
        })
        .catch((error) => {
          this.isLoading = false;
          console.log(error.response.data);
        });
    },

    getLoggedEntity: function () {
      return axios.get('/api/v.1/entity-logged')
        .then((response) => {
          this.loggedUser.cpf_cnpj = response.data.cpf_cnpj;
          this.loggedUser.name = response.data.name;
          this.showLogin = false;
        })
        .catch((error) => {
          if (error.response.status === 422) {
            this.errorLogin = 'CPF/CNPJ ou Senha Inválido!';
            return;
          }
          if (error.response.status === 400) {
            this.errorLogin = 'CPF/CNPJ ou Senha Inválido!';
            return;
          }
          console.log(error.response.data);
        });
    },

    doLogin: function (loginData) {
      this.setLoadingState(true);
      const { cpf_cnpj, password } = loginData;
      return axios.post('/api/v.1/authenticate', {
        cpf_cnpj: cpf_cnpj,
        password: password,
        set_cookie: true,
      })
        .then((response) => {
          this.loggedUser.cpf_cnpj = response.data.cpf_cnpj;
          this.showLogin = false;
          this.setLoadingState(false);
          console.log(response);
          this.cleanAllMensagens();
        })
        .catch((error) => {
          this.setLoadingState(false);
          if (error.response.status === 422) {
            this.errorLogin = 'CPF/CNPJ ou Senha Inválido!';
            return;
          }
          if (error.response.status === 400) {
            this.errorLogin = 'CPF/CNPJ ou Senha Inválido!';
            return;
          }
          console.log(error.response.data);
        });
    },

    doLogout: function () {
      this.setLoadingState(true);
      axios.delete('/api/v.1/authenticate')
        .then((response) => {
          this.showLogin = true;
          console.log(response);
          this.setLoadingState(false);
          this.cleanAllMensagens();
        })
        .catch((error) => {
          this.setLoadingState(false);
          console.log(error);
        });
    },

    doSignUp: function () {
      this.setLoadingState(true);
      const { name, cpf_cnpj, password } = this.signUpData;
      return axios.post('/api/v.1/entity', {
        name: name,
        cpf_cnpj: cpf_cnpj,
        password: password,
      })
        .then((response) => {
          this.setLoadingState(false);
          if (password == "") {
            this.errorSignUp = 'A Senha está inválida!';
            return;
          }
          this.doLogin({
            cpf_cnpj: cpf_cnpj,
            password: password,
          });
          this.cleanAllMensagens();
        })
        .catch((error) => {
          this.setLoadingState(false);
          if (error.response.status === 422) {
            this.errorSignUp = 'CPF/CNPJ está inválido!';
            return;
          }
          if (error.response.status === 400) {
            this.errorSignUp = 'CPF/CNPJ já está cadastrado!';
            return;
          }
          console.log(error);
        });
    },

    getCharges: function (search) {
      this.isLoadingCharge = true;
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
          this.isLoadingCharge = false;
        })
        .catch((error) => {
          this.isLoadingCharge = false;
          if ([404, 422].indexOf(error.response.status) >= 0) {
            this.chargesList = [];
            this.errorCharge = "Pendência Não Encontrada"
            return;
          }
          console.log(error.response.data);
        });
    },

    createCharge: function (chargeData) {
      this.setLoadingState(true);
      chargeData.creditor_cpf_cnpj = this.loggedUser.cpf_cnpj;
      axios.post('/api/v.1/charge', chargeData)
        .then((response) => {
          this.setLoadingState(false);
          if (this.chargeData.debtor.name == "") {
            this.errorCreateCharge = 'Campo nome está vazio.';
            return;
          }
          this.getCharges(this.search);
          this.cleanAllMensagens();
          console.log(response)
        })
        .catch((error) => {
          this.setLoadingState(false);
          if (error.response.status === 422) {
            error_msg = error.response.data.detail[0].msg;
            switch (error_msg) {
              case 'You can not add debt for yourself':
                this.errorCreateCharge = 'Você não pode adicionar débitos para você mesmo.';
                return;

              case 'ensure this value is greater than 0':
                this.errorCreateCharge = 'O valor do débito tem que ser maior que 0.';
                return;

              case 'value is not a valid float':
                this.errorCreateCharge = 'Campo valor está inválido. Exemplo: 100.50';
                return;

              case 'Invalid CPF / CNPJ':
                this.errorCreateCharge = 'CPF/CNPJ inválido.';
                return;

              default:
                this.errorCreateCharge = 'Campos Inválidos.'

            }
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