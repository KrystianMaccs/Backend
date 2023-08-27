(this.webpackJsonpgocreate=this.webpackJsonpgocreate||[]).push([[23],{435:function(e,a,t){"use strict";t.r(a);var n=t(33),c=t(17),r=t(0),l=t.n(r),o=t(378),i=t(306),s=t(310),u=t(311),m=t(297),d=t(319),b=t(334),k=(t(394),t(367)),p=t(379),E=t(325),_=t.n(E),h=t(60),g=t.n(h),B=function(e){var a=e.values,t=a.bank_name,n=a.account_number,c=a.bank_iban,r=a.bank_swift,o=a.route_no,s=a.bank_branch,E=e.errors,h=e.touched,B=e.handleSubmit,v=e.handleChange,f=e.setFieldTouched,y=(e.setFieldValue,e.isValid),N=(Object(k.a)((function(e){return Object(p.a)({formControl:{minWidth:"100%"},selectEmpty:{marginTop:e.spacing(2)}})}))(),function(e,a){a.persist(),v(a),f(e,!0,!1)});return l.a.createElement("form",{onSubmit:B},l.a.createElement(u.a,{className:"text-center card-body-button"},l.a.createElement("div",{className:"card-body-button-wrapper"},l.a.createElement(m.a,{size:"large",type:"submit",disabled:!y,className:"btn-success btn-pill text-nowrap px-5 shadow-none border-3 border-white"},"Update Account Details")),l.a.createElement(i.a,{container:!0,spacing:6},l.a.createElement("div",{className:"scroll-area-lg shadow-overflow pt-6"},l.a.createElement(g.a,{options:{wheelPropagation:!1}},l.a.createElement("div",{className:"p-4 mt-3 container",style:{width:" -webkit-fill-available"}},l.a.createElement(i.a,{container:!0,spacing:3},l.a.createElement(i.a,{item:!0,md:12},l.a.createElement(d.a,{fullWidth:!0,variant:"outlined",id:"bank_name",name:"bank_name",label:"Bank Name",value:t,helperText:h.bank_name?E.bank_name:"",error:h.bank_name&&Boolean(E.bank_name),onChange:N.bind(null,"bank_name"),InputProps:{startAdornment:l.a.createElement(b.a,{position:"start"},l.a.createElement(_.a,null))}})),l.a.createElement(i.a,{item:!0,md:12},l.a.createElement(d.a,{fullWidth:!0,variant:"outlined",id:"bank_branch",name:"bank_branch",label:"Bank Branch",value:s,helperText:h.bank_branch?E.bank_branch:"",error:h.bank_branch&&Boolean(E.bank_branch),onChange:N.bind(null,"bank_branch"),InputProps:{startAdornment:l.a.createElement(b.a,{position:"start"},l.a.createElement(_.a,null))}})),l.a.createElement(i.a,{item:!0,md:12},l.a.createElement(d.a,{fullWidth:!0,variant:"outlined",id:"account_number",name:"account_number",label:"Account Number",value:n,helperText:h.account_number?E.account_number:"",error:h.account_number&&Boolean(E.account_number),onChange:N.bind(null,"account_number"),InputProps:{startAdornment:l.a.createElement(b.a,{position:"start"},l.a.createElement(_.a,null))}})),l.a.createElement(i.a,{item:!0,md:6},l.a.createElement(d.a,{fullWidth:!0,variant:"outlined",id:"bank_iban",name:"bank_iban",label:"Recipient bank\u2019s IBAN (if applicable)",value:c,helperText:h.bank_iban?E.bank_iban:"",error:h.bank_iban&&Boolean(E.bank_iban),onChange:N.bind(null,"bank_iban"),InputProps:{startAdornment:l.a.createElement(b.a,{position:"start"},l.a.createElement(_.a,null))}}))," ",l.a.createElement(i.a,{item:!0,md:6},l.a.createElement(d.a,{fullWidth:!0,variant:"outlined",id:"bank_swift",name:"bank_swift",label:"Recipient bank\u2019s SWIFT or BIC code (if applicable)",value:r,helperText:h.bank_swift?E.bank_swift:"",error:h.bank_swift&&Boolean(E.bank_swift),onChange:N.bind(null,"bank_swift"),InputProps:{startAdornment:l.a.createElement(b.a,{position:"start"},l.a.createElement(_.a,null))}}))," ",l.a.createElement(i.a,{item:!0,md:6},l.a.createElement(d.a,{fullWidth:!0,variant:"outlined",id:"route_no",name:"route_no",label:"Recipient Routing Number",value:o,helperText:h.route_no?E.route_no:"",error:h.route_no&&Boolean(E.route_no),onChange:N.bind(null,"route_no"),InputProps:{startAdornment:l.a.createElement(b.a,{position:"start"},l.a.createElement(_.a,null))}})))))))))},v=(t(124),t(326)),f=t(327),y=t(120),N=t(324),w=function(e){var a,t,n,c,r,u,m,d=e.toggle,b=e.modal,k=e.addBank,p=e.authLoading,E=e.user,_=f.b({bank_name:f.d("").required("Bank Name is required"),account_number:f.d("").required("Account Number is required")}),h={bank_name:null===E||void 0===E||null===(a=E.bank_account)||void 0===a?void 0:a.bank_name,account_number:null===E||void 0===E||null===(t=E.bank_account)||void 0===t?void 0:t.account_number,bank_code:null===E||void 0===E||null===(n=E.bank_account)||void 0===n?void 0:n.bank_code,bank_iban:null===E||void 0===E||null===(c=E.bank_account)||void 0===c?void 0:c.bank_iban,bank_swift:null===E||void 0===E||null===(r=E.bank_account)||void 0===r?void 0:r.bank_swift,route_no:null===E||void 0===E||null===(u=E.bank_account)||void 0===u?void 0:u.route_no,bank_branch:null===E||void 0===E||null===(m=E.bank_account)||void 0===m?void 0:m.bank_branch};return l.a.createElement(o.a,{scroll:"body",maxWidth:"xl",open:b,onClose:d,classes:{paper:"modal-content border-0 bg-white p-xl-0 w-50 p-3"}},l.a.createElement(i.a,{container:!0,style:{width:"100%"}},l.a.createElement(i.a,{item:!0,xs:!0,style:{width:"100%"}},l.a.createElement(N.a,{className:" block-loading-overlay-dark",tag:"div",blocking:p,loader:l.a.createElement(y.ScaleLoader,{color:"var(--white)",loading:p})},l.a.createElement(s.a,null,l.a.createElement("div",{className:"card-img-wrapper"},l.a.createElement("div",{className:"card-badges card-badges-top"},l.a.createElement("div",{className:"badge badge-pill badge-info"},"NEW")),l.a.createElement("div",{className:"bg-composed-wrapper bg-plum-plate border-0"},l.a.createElement("div",{className:"bg-composed-img-2 bg-composed-wrapper--image"}),l.a.createElement("div",{className:"bg-composed-wrapper--content text-center text-white px-2 py-5"},l.a.createElement("h1",{className:"font-size-xxl font-weight-bold py-2 mb-0"},"Update Account Details"),l.a.createElement("p",{className:"mb-2 font-size-lg opacity-7"},"Fill in all the fields to add a Bank your Profile")))),l.a.createElement(v.a,{initialValues:h,validationSchema:_,onSubmit:function(e){e.bank_code=function(e){switch(e){case"Access Bank":case"AccessBank":case"Access":return"044";case"Citibank":case"Citi bank":case"citi":return"023";case"Diamond Bank":case"DiamondBank":case"Diamond":return"063";case"Ecobank Nigeria":case"Ecobank":return"050";case"Fidelity Bank Nigeria":case"FidelityBank ":case"Fidelity Bank ":return"070";case"First Bank of Nigeria":case"First Bank":case"FirstBank":case"FBN":return"011";case"First City Monument Bank":case"FCMB":return"214";case"Guaranty Trust Bank":case"GTB":case"GTBank":return"058";case"Heritage Bank Plc":case"Heritage Bank":case"Heritage":case"HeritageBank":return"030";case"":case"Jaiz Bank":case"JaizBank":case"Jaiz":return"301";case"Keystone Bank Limited":case"KeystoneBank":case"Keystone Bank":case"Keystone":return"082";case"Providus Bank Plc":case"ProvidusBank":case"Providus Bank":case"Providus":return"101";case"Polaris Bank":case"Polaris":case"PolarisBank":return"076";case"Stanbic IBTC Bank Nigeria Limited":case"Stanbic IBTC Bank":case"Stanbic IBTC":case"Stanbic":return"221";case"Standard Chartered Bank":case"StandardChartered ":case"Standard Chartered":return"068";case"Sterling Bank":case"SterlingBank":case"Sterling":return"232";case"Suntrust Bank Nigeria Limited":case"SuntrustBank ":case"Suntrust Bank":case"Suntrust Bank Nigeria":return"100";case"Union Bank of Nigeria":case"UnionBank":case"Union Bank":return"032";case"United Bank of Africa":case"United Bank for Africa":case"UBA":return"033";case"Unity Bank Plc":case"Unity Bank":case"UnityBank":case"Unity":return"215";case"Wema Bank":case"WemaBank":case"Wema":return"035";case"Zenith Bank":case"ZenithBank":case"Zenith":return"057";default:return""}}(e.bank_name),k(e)}},(function(e){return l.a.createElement(B,e)})))))))},x=t(30),P=t(70),A=(t(10),t(339)),C=t(121),S=function(e){var a=e.payment;return l.a.createElement(l.a.Fragment,null,l.a.createElement(s.a,{className:"p-4 shadow-xxl mb-spacing-6-x2 m-4 bg-plum-plate"},l.a.createElement(i.a,{container:!0,spacing:3},l.a.createElement(i.a,{item:!0,md:3},l.a.createElement("div",{className:"card-header--title text-white"},l.a.createElement("b",null,"My Payout Records")," "))),l.a.createElement("div",{className:"table-responsive-md"},l.a.createElement(A.a,{className:"table table-alternate-spaced table-hover text-nowrap"},l.a.createElement("thead",null,l.a.createElement("tr",null,l.a.createElement("th",{scope:"col",className:"text-center"},"#"),l.a.createElement("th",{scope:"col",className:"text-center"},"Title"),l.a.createElement("th",{scope:"col",className:"text-center"},"Net Profit"),l.a.createElement("th",{scope:"col",className:"text-center"},"Gross Profit"),l.a.createElement("th",{scope:"col",className:"text-center"},"Total Deduction"),l.a.createElement("th",{scope:"col",className:"text-center"},"Royalty cut"),l.a.createElement("th",{scope:"col",className:"text-center"}," ","Paid"),l.a.createElement("th",{scope:"col",className:"text-center"},"Failed"),l.a.createElement("th",{scope:"col",className:"text-center"},"Pay Due"),l.a.createElement("th",{scope:"col"}))),l.a.createElement("tbody",null,null===a||void 0===a?void 0:a.results.map((function(e,a){return l.a.createElement(l.a.Fragment,null,l.a.createElement("tr",null,l.a.createElement("td",{className:"text-center text-black-50"},l.a.createElement("span",null,"#",a+1)),l.a.createElement("td",null,l.a.createElement("b",null,e.net_profit)),l.a.createElement("td",null,l.a.createElement("b",null,e.gross_profit)),l.a.createElement("td",null,l.a.createElement("b",null,e.total_deduction)),l.a.createElement("td",null,l.a.createElement("b",null,e.royalty_cut)),l.a.createElement("td",null,l.a.createElement("b",null,e.paid?"Paid":"Not Paid")),l.a.createElement("td",null,l.a.createElement("b",null,e.failed?"Failed":"")),l.a.createElement("td",null,l.a.createElement("b",null,C(e.pay_due).format("YYYY-MM-DD")))),l.a.createElement("tr",{className:"divider"}))})))))))};function F(e){var a=e.toggle,t=e.show;return l.a.createElement(l.a.Fragment,null,l.a.createElement(s.a,{className:"p-5 mb-5 bg-premium-dark"},l.a.createElement("div",{className:"bg-composed-wrapper--content d-block text-center text-xl-left d-xl-flex justify-content-between align-items-center"},l.a.createElement("div",{className:"text-white"},l.a.createElement("h5",{className:"display-4 font-weight-bold mb-3"},"Add your bank account to your Gocreate profile."),l.a.createElement("p",{className:"font-size-lg opacity-7 mb-4"},"In order for you to be able to execute transactions, you will need to add a valid bank account."),l.a.createElement(m.a,{className:"btn-success",onClick:a},t?" Add Bank Account":"Update Bank Account")))))}a.default=Object(c.connect)((function(e){return{authLoading:e.auth.authLoading,payment:e.payment.payment,user:e.auth.user}}),(function(e){return{addBank:function(a){return e(x.c(a))}}}))((function(e){var a=e.user,t=e.addBank,c=e.authLoading,o=e.payment,i=Object(r.useState)(!1),s=Object(n.a)(i,2),u=s[0],d=s[1],b=function(){return d(!u)},k=!a.bank_account.bank_name&&!a.bank_account.bank_account&&!a.bank_account.bank_iban&&!a.bank_account.bank_swift&&!a.bank_account.route_no&&!a.bank_account.bank_branch;return l.a.createElement("div",null,l.a.createElement(P.c,{titleHeading:"Payout",titleDescription:"Link your Bank to your Account and  View Your Payout History"}," ",l.a.createElement(m.a,{onClick:b,className:"btn-primary m-2"},k?"Add Bank":"Update Bank"),l.a.createElement(w,{user:a,modal:u,toggle:b,addBank:t,authLoading:c})),l.a.createElement(F,{toggle:b,show:k}),l.a.createElement(S,{payment:o}))}))}}]);