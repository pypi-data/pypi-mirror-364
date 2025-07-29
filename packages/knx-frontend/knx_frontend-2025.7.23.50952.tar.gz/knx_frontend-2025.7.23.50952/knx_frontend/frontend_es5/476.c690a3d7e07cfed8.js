"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["476"],{49590:function(e,t,i){i.a(e,(async function(e,o){try{i.r(t),i.d(t,{HaIconPicker:()=>w});i(39710),i(26847),i(2394),i(18574),i(81738),i(94814),i(22960),i(6989),i(72489),i(1455),i(67886),i(65451),i(46015),i(38334),i(94880),i(75643),i(29761),i(56389),i(27530);var a=i(73742),s=i(59048),r=i(7616),n=i(28105),l=i(29740),c=i(18610),h=i(54693),d=(i(3847),i(57264),e([h]));h=(d.then?(await d)():d)[0];let u,p,_,v,g,b=e=>e,m=[],y=!1;const f=async()=>{y=!0;const e=await i.e("4813").then(i.t.bind(i,81405,19));m=e.default.map((e=>({icon:`mdi:${e.name}`,parts:new Set(e.name.split("-")),keywords:e.keywords})));const t=[];Object.keys(c.g).forEach((e=>{t.push($(e))})),(await Promise.all(t)).forEach((e=>{m.push(...e)}))},$=async e=>{try{const t=c.g[e].getIconList;if("function"!=typeof t)return[];const i=await t();return i.map((t=>{var i;return{icon:`${e}:${t.name}`,parts:new Set(t.name.split("-")),keywords:null!==(i=t.keywords)&&void 0!==i?i:[]}}))}catch(t){return console.warn(`Unable to load icon list for ${e} iconset`),[]}},k=e=>(0,s.dy)(u||(u=b`
  <ha-combo-box-item type="button">
    <ha-icon .icon=${0} slot="start"></ha-icon>
    ${0}
  </ha-combo-box-item>
`),e.icon,e.icon);class w extends s.oi{render(){return(0,s.dy)(p||(p=b`
      <ha-combo-box
        .hass=${0}
        item-value-path="icon"
        item-label-path="icon"
        .value=${0}
        allow-custom-value
        .dataProvider=${0}
        .label=${0}
        .helper=${0}
        .disabled=${0}
        .required=${0}
        .placeholder=${0}
        .errorMessage=${0}
        .invalid=${0}
        .renderer=${0}
        icon
        @opened-changed=${0}
        @value-changed=${0}
      >
        ${0}
      </ha-combo-box>
    `),this.hass,this._value,y?this._iconProvider:void 0,this.label,this.helper,this.disabled,this.required,this.placeholder,this.errorMessage,this.invalid,k,this._openedChanged,this._valueChanged,this._value||this.placeholder?(0,s.dy)(_||(_=b`
              <ha-icon .icon=${0} slot="icon">
              </ha-icon>
            `),this._value||this.placeholder):(0,s.dy)(v||(v=b`<slot slot="icon" name="fallback"></slot>`)))}async _openedChanged(e){e.detail.value&&!y&&(await f(),this.requestUpdate())}_valueChanged(e){e.stopPropagation(),this._setValue(e.detail.value)}_setValue(e){this.value=e,(0,l.B)(this,"value-changed",{value:this._value},{bubbles:!1,composed:!1})}get _value(){return this.value||""}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.invalid=!1,this._filterIcons=(0,n.Z)(((e,t=m)=>{if(!e)return t;const i=[],o=(e,t)=>i.push({icon:e,rank:t});for(const a of t)a.parts.has(e)?o(a.icon,1):a.keywords.includes(e)?o(a.icon,2):a.icon.includes(e)?o(a.icon,3):a.keywords.some((t=>t.includes(e)))&&o(a.icon,4);return 0===i.length&&o(e,0),i.sort(((e,t)=>e.rank-t.rank))})),this._iconProvider=(e,t)=>{const i=this._filterIcons(e.filter.toLowerCase(),m),o=e.page*e.pageSize,a=o+e.pageSize;t(i.slice(o,a),i.length)}}}w.styles=(0,s.iv)(g||(g=b`
    *[slot="icon"] {
      color: var(--primary-text-color);
      position: relative;
      bottom: 2px;
    }
    *[slot="prefix"] {
      margin-right: 8px;
      margin-inline-end: 8px;
      margin-inline-start: initial;
    }
  `)),(0,a.__decorate)([(0,r.Cb)({attribute:!1})],w.prototype,"hass",void 0),(0,a.__decorate)([(0,r.Cb)()],w.prototype,"value",void 0),(0,a.__decorate)([(0,r.Cb)()],w.prototype,"label",void 0),(0,a.__decorate)([(0,r.Cb)()],w.prototype,"helper",void 0),(0,a.__decorate)([(0,r.Cb)()],w.prototype,"placeholder",void 0),(0,a.__decorate)([(0,r.Cb)({attribute:"error-message"})],w.prototype,"errorMessage",void 0),(0,a.__decorate)([(0,r.Cb)({type:Boolean})],w.prototype,"disabled",void 0),(0,a.__decorate)([(0,r.Cb)({type:Boolean})],w.prototype,"required",void 0),(0,a.__decorate)([(0,r.Cb)({type:Boolean})],w.prototype,"invalid",void 0),w=(0,a.__decorate)([(0,r.Mo)("ha-icon-picker")],w),o()}catch(u){o(u)}}))},26440:function(e,t,i){i.a(e,(async function(e,o){try{i.r(t);i(26847),i(87799),i(27530);var a=i(73742),s=i(59048),r=i(7616),n=i(29740),l=(i(86776),i(74207),i(49590)),c=(i(38573),i(77204)),h=e([l]);l=(h.then?(await h)():h)[0];let d,u,p=e=>e;class _ extends s.oi{set item(e){this._item=e,e?(this._name=e.name||"",this._icon=e.icon||"",this._duration=e.duration||"00:00:00",this._restore=e.restore||!1):(this._name="",this._icon="",this._duration="00:00:00",this._restore=!1)}focus(){this.updateComplete.then((()=>{var e;return null===(e=this.shadowRoot)||void 0===e||null===(e=e.querySelector("[dialogInitialFocus]"))||void 0===e?void 0:e.focus()}))}render(){return this.hass?(0,s.dy)(d||(d=p`
      <div class="form">
        <ha-textfield
          .value=${0}
          .configValue=${0}
          @input=${0}
          .label=${0}
          autoValidate
          required
          .validationMessage=${0}
          dialogInitialFocus
        ></ha-textfield>
        <ha-icon-picker
          .hass=${0}
          .value=${0}
          .configValue=${0}
          @value-changed=${0}
          .label=${0}
        ></ha-icon-picker>
        <ha-textfield
          .configValue=${0}
          .value=${0}
          @input=${0}
          .label=${0}
        ></ha-textfield>
        <ha-formfield
          .label=${0}
        >
          <ha-checkbox
            .configValue=${0}
            .checked=${0}
            @click=${0}
          >
          </ha-checkbox>
        </ha-formfield>
      </div>
    `),this._name,"name",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.name"),this.hass.localize("ui.dialogs.helper_settings.required_error_msg"),this.hass,this._icon,"icon",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.icon"),"duration",this._duration,this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.timer.duration"),this.hass.localize("ui.dialogs.helper_settings.timer.restore"),"restore",this._restore,this._toggleRestore):s.Ld}_valueChanged(e){var t;if(!this.new&&!this._item)return;e.stopPropagation();const i=e.target.configValue,o=(null===(t=e.detail)||void 0===t?void 0:t.value)||e.target.value;if(this[`_${i}`]===o)return;const a=Object.assign({},this._item);o?a[i]=o:delete a[i],(0,n.B)(this,"value-changed",{value:a})}_toggleRestore(){this._restore=!this._restore,(0,n.B)(this,"value-changed",{value:Object.assign(Object.assign({},this._item),{},{restore:this._restore})})}static get styles(){return[c.Qx,(0,s.iv)(u||(u=p`
        .form {
          color: var(--primary-text-color);
        }
        ha-textfield {
          display: block;
          margin: 8px 0;
        }
      `))]}constructor(...e){super(...e),this.new=!1}}(0,a.__decorate)([(0,r.Cb)({attribute:!1})],_.prototype,"hass",void 0),(0,a.__decorate)([(0,r.Cb)({type:Boolean})],_.prototype,"new",void 0),(0,a.__decorate)([(0,r.SB)()],_.prototype,"_name",void 0),(0,a.__decorate)([(0,r.SB)()],_.prototype,"_icon",void 0),(0,a.__decorate)([(0,r.SB)()],_.prototype,"_duration",void 0),(0,a.__decorate)([(0,r.SB)()],_.prototype,"_restore",void 0),_=(0,a.__decorate)([(0,r.Mo)("ha-timer-form")],_),o()}catch(d){o(d)}}))}}]);
//# sourceMappingURL=476.c690a3d7e07cfed8.js.map