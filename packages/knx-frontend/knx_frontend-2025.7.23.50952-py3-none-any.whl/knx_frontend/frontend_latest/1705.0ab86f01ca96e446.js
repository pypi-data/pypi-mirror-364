export const __webpack_ids__=["1705"];export const __webpack_modules__={24393:function(e,t,i){i.d(t,{v:()=>a});const a=async(e,t)=>{if(navigator.clipboard)try{return void(await navigator.clipboard.writeText(e))}catch{}const i=t??document.body,a=document.createElement("textarea");a.value=e,i.appendChild(a),a.select(),document.execCommand("copy"),i.removeChild(a)}},58762:function(e,t,i){var a=i(73742),s=i(59048),o=i(7616),n=i(28105),r=i(29740),d=i(41806);i(3847);const l={key:"Mod-s",run:e=>((0,r.B)(e.dom,"editor-save"),!0)},p=e=>{const t=document.createElement("ha-icon");return t.icon=e.label,t};class h extends s.fl{set value(e){this._value=e}get value(){return this.codemirror?this.codemirror.state.doc.toString():this._value}get hasComments(){if(!this.codemirror||!this._loadedCodeMirror)return!1;const e=this._loadedCodeMirror.highlightingFor(this.codemirror.state,[this._loadedCodeMirror.tags.comment]);return!!this.renderRoot.querySelector(`span.${e}`)}connectedCallback(){super.connectedCallback(),this.hasUpdated&&this.requestUpdate(),this.addEventListener("keydown",d.U),this.codemirror&&!1!==this.autofocus&&this.codemirror.focus()}disconnectedCallback(){super.disconnectedCallback(),this.removeEventListener("keydown",d.U),this.updateComplete.then((()=>{this.codemirror.destroy(),delete this.codemirror}))}async scheduleUpdate(){this._loadedCodeMirror??=await Promise.all([i.e("5192"),i.e("4547")]).then(i.bind(i,13618)),super.scheduleUpdate()}update(e){if(super.update(e),!this.codemirror)return void this._createCodeMirror();const t=[];e.has("mode")&&t.push({effects:[this._loadedCodeMirror.langCompartment.reconfigure(this._mode),this._loadedCodeMirror.foldingCompartment.reconfigure(this._getFoldingExtensions())]}),e.has("readOnly")&&t.push({effects:this._loadedCodeMirror.readonlyCompartment.reconfigure(this._loadedCodeMirror.EditorView.editable.of(!this.readOnly))}),e.has("linewrap")&&t.push({effects:this._loadedCodeMirror.linewrapCompartment.reconfigure(this.linewrap?this._loadedCodeMirror.EditorView.lineWrapping:[])}),e.has("_value")&&this._value!==this.value&&t.push({changes:{from:0,to:this.codemirror.state.doc.length,insert:this._value}}),t.length>0&&this.codemirror.dispatch(...t),e.has("error")&&this.classList.toggle("error-state",this.error)}get _mode(){return this._loadedCodeMirror.langs[this.mode]}_createCodeMirror(){if(!this._loadedCodeMirror)throw new Error("Cannot create editor before CodeMirror is loaded");const e=[this._loadedCodeMirror.lineNumbers(),this._loadedCodeMirror.history(),this._loadedCodeMirror.drawSelection(),this._loadedCodeMirror.EditorState.allowMultipleSelections.of(!0),this._loadedCodeMirror.rectangularSelection(),this._loadedCodeMirror.crosshairCursor(),this._loadedCodeMirror.highlightSelectionMatches(),this._loadedCodeMirror.highlightActiveLine(),this._loadedCodeMirror.indentationMarkers({thickness:0,activeThickness:1,colors:{activeLight:"var(--secondary-text-color)",activeDark:"var(--secondary-text-color)"}}),this._loadedCodeMirror.keymap.of([...this._loadedCodeMirror.defaultKeymap,...this._loadedCodeMirror.searchKeymap,...this._loadedCodeMirror.historyKeymap,...this._loadedCodeMirror.tabKeyBindings,l]),this._loadedCodeMirror.langCompartment.of(this._mode),this._loadedCodeMirror.haTheme,this._loadedCodeMirror.haSyntaxHighlighting,this._loadedCodeMirror.readonlyCompartment.of(this._loadedCodeMirror.EditorView.editable.of(!this.readOnly)),this._loadedCodeMirror.linewrapCompartment.of(this.linewrap?this._loadedCodeMirror.EditorView.lineWrapping:[]),this._loadedCodeMirror.EditorView.updateListener.of(this._onUpdate),this._loadedCodeMirror.foldingCompartment.of(this._getFoldingExtensions())];if(!this.readOnly){const t=[];this.autocompleteEntities&&this.hass&&t.push(this._entityCompletions.bind(this)),this.autocompleteIcons&&t.push(this._mdiCompletions.bind(this)),t.length>0&&e.push(this._loadedCodeMirror.autocompletion({override:t,maxRenderedOptions:10}))}this.codemirror=new this._loadedCodeMirror.EditorView({state:this._loadedCodeMirror.EditorState.create({doc:this._value,extensions:e}),parent:this.renderRoot})}_entityCompletions(e){const t=e.matchBefore(/[a-z_]{3,}\.\w*/);if(!t||t.from===t.to&&!e.explicit)return null;const i=this._getStates(this.hass.states);return i&&i.length?{from:Number(t.from),options:i,validFor:/^[a-z_]{3,}\.\w*$/}:null}async _mdiCompletions(e){const t=e.matchBefore(/mdi:\S*/);if(!t||t.from===t.to&&!e.explicit)return null;const i=await this._getIconItems();return{from:Number(t.from),options:i,validFor:/^mdi:\S*$/}}constructor(...e){super(...e),this.mode="yaml",this.autofocus=!1,this.readOnly=!1,this.linewrap=!1,this.autocompleteEntities=!1,this.autocompleteIcons=!1,this.error=!1,this._value="",this._getStates=(0,n.Z)((e=>{if(!e)return[];return Object.keys(e).map((t=>({type:"variable",label:t,detail:e[t].attributes.friendly_name,info:`State: ${e[t].state}`})))})),this._getIconItems=async()=>{if(!this._iconList){let e;e=(await i.e("4813").then(i.t.bind(i,81405,19))).default,this._iconList=e.map((e=>({type:"variable",label:`mdi:${e.name}`,detail:e.keywords.join(", "),info:p})))}return this._iconList},this._onUpdate=e=>{e.docChanged&&(this._value=e.state.doc.toString(),(0,r.B)(this,"value-changed",{value:this._value}))},this._getFoldingExtensions=()=>"yaml"===this.mode?[this._loadedCodeMirror.foldGutter(),this._loadedCodeMirror.foldingOnIndent]:[]}}h.styles=s.iv`
    :host(.error-state) .cm-gutters {
      border-color: var(--error-state-color, red);
    }
  `,(0,a.__decorate)([(0,o.Cb)()],h.prototype,"mode",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],h.prototype,"autofocus",void 0),(0,a.__decorate)([(0,o.Cb)({attribute:"read-only",type:Boolean})],h.prototype,"readOnly",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],h.prototype,"linewrap",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean,attribute:"autocomplete-entities"})],h.prototype,"autocompleteEntities",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean,attribute:"autocomplete-icons"})],h.prototype,"autocompleteIcons",void 0),(0,a.__decorate)([(0,o.Cb)({type:Boolean})],h.prototype,"error",void 0),(0,a.__decorate)([(0,o.SB)()],h.prototype,"_value",void 0),h=(0,a.__decorate)([(0,o.Mo)("ha-code-editor")],h)},36344:function(e,t,i){var a=i(73742),s=i(24110),o=i(59048),n=i(7616),r=i(29740),d=i(77204),l=(i(58762),i(15606)),p=i(24393);i(30337);class h extends o.oi{setValue(e){try{this._yaml=(e=>{if("object"!=typeof e||null===e)return!1;for(const t in e)if(Object.prototype.hasOwnProperty.call(e,t))return!1;return!0})(e)?"":(0,s.$w)(e,{schema:this.yamlSchema,quotingType:'"',noRefs:!0})}catch(t){console.error(t,e),alert(`There was an error converting to YAML: ${t}`)}}firstUpdated(){void 0!==this.defaultValue&&this.setValue(this.defaultValue)}willUpdate(e){super.willUpdate(e),this.autoUpdate&&e.has("value")&&this.setValue(this.value)}focus(){this._codeEditor?.codemirror&&this._codeEditor?.codemirror.focus()}render(){return void 0===this._yaml?o.Ld:o.dy`
      ${this.label?o.dy`<p>${this.label}${this.required?" *":""}</p>`:o.Ld}
      <ha-code-editor
        .hass=${this.hass}
        .value=${this._yaml}
        .readOnly=${this.readOnly}
        mode="yaml"
        autocomplete-entities
        autocomplete-icons
        .error=${!1===this.isValid}
        @value-changed=${this._onChange}
        dir="ltr"
      ></ha-code-editor>
      ${this.copyClipboard||this.hasExtraActions?o.dy`
            <div class="card-actions">
              ${this.copyClipboard?o.dy`
                    <ha-button @click=${this._copyYaml}>
                      ${this.hass.localize("ui.components.yaml-editor.copy_to_clipboard")}
                    </ha-button>
                  `:o.Ld}
              <slot name="extra-actions"></slot>
            </div>
          `:o.Ld}
    `}_onChange(e){let t;e.stopPropagation(),this._yaml=e.detail.value;let i,a=!0;if(this._yaml)try{t=(0,s.zD)(this._yaml,{schema:this.yamlSchema})}catch(o){a=!1,i=`${this.hass.localize("ui.components.yaml-editor.error",{reason:o.reason})}${o.mark?` (${this.hass.localize("ui.components.yaml-editor.error_location",{line:o.mark.line+1,column:o.mark.column+1})})`:""}`}else t={};this.value=t,this.isValid=a,(0,r.B)(this,"value-changed",{value:t,isValid:a,errorMsg:i})}get yaml(){return this._yaml}async _copyYaml(){this.yaml&&(await(0,p.v)(this.yaml),(0,l.C)(this,{message:this.hass.localize("ui.common.copied_clipboard")}))}static get styles(){return[d.Qx,o.iv`
        .card-actions {
          border-radius: var(
            --actions-border-radius,
            0px 0px var(--ha-card-border-radius, 12px)
              var(--ha-card-border-radius, 12px)
          );
          border: 1px solid var(--divider-color);
          padding: 5px 16px;
        }
        ha-code-editor {
          flex-grow: 1;
        }
      `]}constructor(...e){super(...e),this.yamlSchema=s.oW,this.isValid=!0,this.autoUpdate=!1,this.readOnly=!1,this.required=!1,this.copyClipboard=!1,this.hasExtraActions=!1,this._yaml=""}}(0,a.__decorate)([(0,n.Cb)({attribute:!1})],h.prototype,"hass",void 0),(0,a.__decorate)([(0,n.Cb)()],h.prototype,"value",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],h.prototype,"yamlSchema",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:!1})],h.prototype,"defaultValue",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:"is-valid",type:Boolean})],h.prototype,"isValid",void 0),(0,a.__decorate)([(0,n.Cb)()],h.prototype,"label",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:"auto-update",type:Boolean})],h.prototype,"autoUpdate",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:"read-only",type:Boolean})],h.prototype,"readOnly",void 0),(0,a.__decorate)([(0,n.Cb)({type:Boolean})],h.prototype,"required",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:"copy-clipboard",type:Boolean})],h.prototype,"copyClipboard",void 0),(0,a.__decorate)([(0,n.Cb)({attribute:"has-extra-actions",type:Boolean})],h.prototype,"hasExtraActions",void 0),(0,a.__decorate)([(0,n.SB)()],h.prototype,"_yaml",void 0),(0,a.__decorate)([(0,n.IO)("ha-code-editor")],h.prototype,"_codeEditor",void 0),h=(0,a.__decorate)([(0,n.Mo)("ha-yaml-editor")],h)},10929:function(e,t,i){var a=i(73742),s=i(59048),o=i(7616),n=i(28105);i(91337);class r extends s.oi{async focus(){await this.updateComplete;const e=this.renderRoot?.querySelector("ha-form");e?.focus()}render(){return s.dy`
      <div class="section">
        <div class="intro">
          <h3>
            ${this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.config.title")}
          </h3>
          <p>
            ${this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.config.description")}
          </p>
        </div>
        <ha-form
          .schema=${this._schema(this.supportedLanguages)}
          .data=${this.data}
          .hass=${this.hass}
          .computeLabel=${this._computeLabel}
        ></ha-form>
      </div>
    `}constructor(...e){super(...e),this._schema=(0,n.Z)((e=>[{name:"",type:"grid",schema:[{name:"name",required:!0,selector:{text:{}}},e?{name:"language",required:!0,selector:{language:{languages:e}}}:{name:"",type:"constant"}]}])),this._computeLabel=e=>e.name?this.hass.localize(`ui.panel.config.voice_assistants.assistants.pipeline.detail.form.${e.name}`):""}}r.styles=s.iv`
    .section {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      box-sizing: border-box;
      padding: 16px;
    }
    .intro {
      margin-bottom: 16px;
    }
    h3 {
      font-size: var(--ha-font-size-xl);
      font-weight: var(--ha-font-weight-normal);
      line-height: var(--ha-line-height-condensed);
      margin-top: 0;
      margin-bottom: 4px;
    }
    p {
      color: var(--secondary-text-color);
      font-size: var(--mdc-typography-body2-font-size, var(--ha-font-size-s));
      margin-top: 0;
      margin-bottom: 0;
    }
  `,(0,a.__decorate)([(0,o.Cb)({attribute:!1})],r.prototype,"hass",void 0),(0,a.__decorate)([(0,o.Cb)({attribute:!1})],r.prototype,"data",void 0),(0,a.__decorate)([(0,o.Cb)({attribute:!1,type:Array})],r.prototype,"supportedLanguages",void 0),r=(0,a.__decorate)([(0,o.Mo)("assist-pipeline-detail-config")],r)},44618:function(e,t,i){var a=i(73742),s=i(59048),o=i(7616),n=i(28105),r=(i(91337),i(29740));class d extends s.oi{render(){return s.dy`
      <div class="section">
        <div class="intro">
          <h3>
            ${this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.conversation.title")}
          </h3>
          <p>
            ${this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.conversation.description")}
          </p>
        </div>
        <ha-form
          .schema=${this._schema(this.data?.conversation_engine,this.data?.language,this._supportedLanguages)}
          .data=${this.data}
          .hass=${this.hass}
          .computeLabel=${this._computeLabel}
          .computeHelper=${this._computeHelper}
          @supported-languages-changed=${this._supportedLanguagesChanged}
        ></ha-form>
      </div>
    `}_supportedLanguagesChanged(e){"*"===e.detail.value&&setTimeout((()=>{const e={...this.data};e.conversation_language="*",(0,r.B)(this,"value-changed",{value:e})}),0),this._supportedLanguages=e.detail.value}constructor(...e){super(...e),this._schema=(0,n.Z)(((e,t,i)=>{const a=[{name:"",type:"grid",schema:[{name:"conversation_engine",required:!0,selector:{conversation_agent:{language:t}}}]}];return"*"!==i&&i?.length&&a[0].schema.push({name:"conversation_language",required:!0,selector:{language:{languages:i,no_sort:!0}}}),"conversation.home_assistant"!==e&&a.push({name:"prefer_local_intents",default:!0,selector:{boolean:{}}}),a})),this._computeLabel=e=>e.name?this.hass.localize(`ui.panel.config.voice_assistants.assistants.pipeline.detail.form.${e.name}`):"",this._computeHelper=e=>e.name?this.hass.localize(`ui.panel.config.voice_assistants.assistants.pipeline.detail.form.${e.name}_description`):""}}d.styles=s.iv`
    .section {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      box-sizing: border-box;
      padding: 16px;
    }
    .intro {
      margin-bottom: 16px;
    }
    h3 {
      font-size: var(--ha-font-size-xl);
      font-weight: var(--ha-font-weight-normal);
      line-height: var(--ha-line-height-condensed);
      margin-top: 0;
      margin-bottom: 4px;
    }
    p {
      color: var(--secondary-text-color);
      font-size: var(--mdc-typography-body2-font-size, var(--ha-font-size-s));
      margin-top: 0;
      margin-bottom: 0;
    }
  `,(0,a.__decorate)([(0,o.Cb)({attribute:!1})],d.prototype,"hass",void 0),(0,a.__decorate)([(0,o.Cb)({attribute:!1})],d.prototype,"data",void 0),(0,a.__decorate)([(0,o.SB)()],d.prototype,"_supportedLanguages",void 0),d=(0,a.__decorate)([(0,o.Mo)("assist-pipeline-detail-conversation")],d)},11011:function(e,t,i){var a=i(73742),s=i(59048),o=i(7616),n=i(28105);i(91337);class r extends s.oi{render(){return s.dy`
      <div class="section">
        <div class="intro">
          <h3>
            ${this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.stt.title")}
          </h3>
          <p>
            ${this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.stt.description")}
          </p>
        </div>
        <ha-form
          .schema=${this._schema(this.data?.language,this._supportedLanguages)}
          .data=${this.data}
          .hass=${this.hass}
          .computeLabel=${this._computeLabel}
          @supported-languages-changed=${this._supportedLanguagesChanged}
        ></ha-form>
      </div>
    `}_supportedLanguagesChanged(e){this._supportedLanguages=e.detail.value}constructor(...e){super(...e),this._schema=(0,n.Z)(((e,t)=>[{name:"",type:"grid",schema:[{name:"stt_engine",selector:{stt:{language:e}}},t?.length?{name:"stt_language",required:!0,selector:{language:{languages:t,no_sort:!0}}}:{name:"",type:"constant"}]}])),this._computeLabel=e=>e.name?this.hass.localize(`ui.panel.config.voice_assistants.assistants.pipeline.detail.form.${e.name}`):""}}r.styles=s.iv`
    .section {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
      box-sizing: border-box;
      padding: 16px;
    }
    .intro {
      margin-bottom: 16px;
    }
    h3 {
      font-size: var(--ha-font-size-xl);
      font-weight: var(--ha-font-weight-normal);
      line-height: var(--ha-line-height-condensed);
      margin-top: 0;
      margin-bottom: 4px;
    }
    p {
      color: var(--secondary-text-color);
      font-size: var(--mdc-typography-body2-font-size, var(--ha-font-size-s));
      margin-top: 0;
      margin-bottom: 0;
    }
  `,(0,a.__decorate)([(0,o.Cb)({attribute:!1})],r.prototype,"hass",void 0),(0,a.__decorate)([(0,o.Cb)({attribute:!1})],r.prototype,"data",void 0),(0,a.__decorate)([(0,o.SB)()],r.prototype,"_supportedLanguages",void 0),r=(0,a.__decorate)([(0,o.Mo)("assist-pipeline-detail-stt")],r)},2994:function(e,t,i){var a=i(73742),s=i(59048),o=i(7616),n=i(28105),r=(i(30337),i(91337),i(29740));const d=()=>i.e("9952").then(i.bind(i,54695));class l extends s.oi{render(){return s.dy`
      <div class="section">
        <div class="content">
          <div class="intro">
          <h3>
            ${this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.tts.title")}
          </h3>
          <p>
            ${this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.tts.description")}
          </p>
          </div>
          <ha-form
            .schema=${this._schema(this.data?.language,this._supportedLanguages)}
            .data=${this.data}
            .hass=${this.hass}
            .computeLabel=${this._computeLabel}
            @supported-languages-changed=${this._supportedLanguagesChanged}
          ></ha-form>
        </div>

       ${this.data?.tts_engine?s.dy`<div class="footer">
               <ha-button
                 .label=${this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.try_tts")}
                 @click=${this._preview}
               >
               </ha-button>
             </div>`:s.Ld}
        </div>
      </div>
    `}async _preview(){if(!this.data)return;const e=this.data.tts_engine,t=this.data.tts_language||void 0,i=this.data.tts_voice||void 0;var a,s;e&&(a=this,s={engine:e,language:t,voice:i},(0,r.B)(a,"show-dialog",{addHistory:!1,dialogTag:"dialog-tts-try",dialogImport:d,dialogParams:s}))}_supportedLanguagesChanged(e){this._supportedLanguages=e.detail.value}constructor(...e){super(...e),this._schema=(0,n.Z)(((e,t)=>[{name:"",type:"grid",schema:[{name:"tts_engine",selector:{tts:{language:e}}},t?.length?{name:"tts_language",required:!0,selector:{language:{languages:t,no_sort:!0}}}:{name:"",type:"constant"},{name:"tts_voice",selector:{tts_voice:{}},context:{language:"tts_language",engineId:"tts_engine"},required:!0}]}])),this._computeLabel=e=>e.name?this.hass.localize(`ui.panel.config.voice_assistants.assistants.pipeline.detail.form.${e.name}`):""}}l.styles=s.iv`
    .section {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
    }
    .content {
      padding: 16px;
    }
    .intro {
      margin-bottom: 16px;
    }
    h3 {
      font-size: var(--ha-font-size-xl);
      font-weight: var(--ha-font-weight-normal);
      line-height: var(--ha-line-height-condensed);
      margin-top: 0;
      margin-bottom: 4px;
    }
    p {
      color: var(--secondary-text-color);
      font-size: var(--mdc-typography-body2-font-size, var(--ha-font-size-s));
      margin-top: 0;
      margin-bottom: 0;
    }
    .footer {
      border-top: 1px solid var(--divider-color);
      padding: 8px 16px;
    }
  `,(0,a.__decorate)([(0,o.Cb)({attribute:!1})],l.prototype,"hass",void 0),(0,a.__decorate)([(0,o.Cb)({attribute:!1})],l.prototype,"data",void 0),(0,a.__decorate)([(0,o.SB)()],l.prototype,"_supportedLanguages",void 0),l=(0,a.__decorate)([(0,o.Mo)("assist-pipeline-detail-tts")],l)},7235:function(e,t,i){var a=i(73742),s=i(59048),o=i(7616),n=i(28105);i(91337);var r=i(29740);class d extends s.oi{willUpdate(e){e.has("data")&&e.get("data")?.wake_word_entity!==this.data?.wake_word_entity&&(e.get("data")?.wake_word_entity&&this.data?.wake_word_id&&(0,r.B)(this,"value-changed",{value:{...this.data,wake_word_id:void 0}}),this._fetchWakeWords())}render(){return s.dy`
      <div class="section">
        <div class="content">
          <div class="intro">
            <h3>
              ${this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.wakeword.title")}
            </h3>
            <p>
              ${this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.wakeword.description")}
            </p>
            <ha-alert alert-type="info">
              ${this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.steps.wakeword.note")}
            </ha-alert>
          </div>
          <ha-form
            .schema=${this._schema(this._wakeWords)}
            .data=${this.data}
            .hass=${this.hass}
            .computeLabel=${this._computeLabel}
          ></ha-form>
        </div>
      </div>
    `}async _fetchWakeWords(){if(this._wakeWords=void 0,!this.data?.wake_word_entity)return;const e=this.data.wake_word_entity,t=await(i=this.hass,a=e,i.callWS({type:"wake_word/info",entity_id:a}));var i,a;this.data.wake_word_entity===e&&(this._wakeWords=t.wake_words,!this.data||this.data?.wake_word_id&&this._wakeWords.some((e=>e.id===this.data.wake_word_id))||(0,r.B)(this,"value-changed",{value:{...this.data,wake_word_id:this._wakeWords[0]?.id}}))}constructor(...e){super(...e),this._schema=(0,n.Z)((e=>[{name:"",type:"grid",schema:[{name:"wake_word_entity",selector:{entity:{domain:"wake_word"}}},e?.length?{name:"wake_word_id",required:!0,selector:{select:{mode:"dropdown",sort:!0,options:e.map((e=>({value:e.id,label:e.name})))}}}:{name:"",type:"constant"}]}])),this._computeLabel=e=>e.name?this.hass.localize(`ui.panel.config.voice_assistants.assistants.pipeline.detail.form.${e.name}`):""}}d.styles=s.iv`
    .section {
      border: 1px solid var(--divider-color);
      border-radius: 8px;
    }
    .content {
      padding: 16px;
    }
    .intro {
      margin-bottom: 16px;
    }
    h3 {
      font-size: var(--ha-font-size-xl);
      font-weight: var(--ha-font-weight-normal);
      line-height: var(--ha-line-height-condensed);
      margin-top: 0;
      margin-bottom: 4px;
    }
    p {
      color: var(--secondary-text-color);
      font-size: var(--mdc-typography-body2-font-size, var(--ha-font-size-s));
      margin-top: 0;
      margin-bottom: 0;
    }
    a {
      color: var(--primary-color);
    }
  `,(0,a.__decorate)([(0,o.Cb)({attribute:!1})],d.prototype,"hass",void 0),(0,a.__decorate)([(0,o.Cb)({attribute:!1})],d.prototype,"data",void 0),(0,a.__decorate)([(0,o.SB)()],d.prototype,"_wakeWords",void 0),d=(0,a.__decorate)([(0,o.Mo)("assist-pipeline-detail-wakeword")],d)},30227:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(73742),s=i(59048),o=i(7616),n=i(28105),r=i(32518),d=i(83989),l=e([d]);d=(l.then?(await l)():l)[0];class p extends s.oi{render(){const e=this._processEvents(this.events);return e?s.dy`
      <assist-render-pipeline-run
        .hass=${this.hass}
        .pipelineRun=${e}
      ></assist-render-pipeline-run>
    `:this.events.length?s.dy`<ha-alert alert-type="error">Error showing run</ha-alert>
          <ha-card>
            <ha-expansion-panel>
              <span slot="header">Raw</span>
              <pre>${JSON.stringify(this.events,null,2)}</pre>
            </ha-expansion-panel>
          </ha-card>`:s.dy`<ha-alert alert-type="warning"
        >There were no events in this run.</ha-alert
      >`}constructor(...e){super(...e),this._processEvents=(0,n.Z)((e=>{let t;return e.forEach((e=>{t=(0,r.eP)(t,e)})),t}))}}(0,a.__decorate)([(0,o.Cb)({attribute:!1})],p.prototype,"hass",void 0),(0,a.__decorate)([(0,o.Cb)({attribute:!1})],p.prototype,"events",void 0),p=(0,a.__decorate)([(0,o.Mo)("assist-render-pipeline-events")],p),t()}catch(p){t(p)}}))},83989:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(73742),s=i(59048),o=i(7616),n=(i(13965),i(22543),i(30337),i(97862)),r=(i(86932),i(53303)),d=(i(36344),i(81665)),l=e([n,r]);[n,r]=l.then?(await l)():l;const p={pipeline:"Pipeline",language:"Language"},h={engine:"Engine"},c={engine:"Engine"},u={engine:"Engine",language:"Language",intent_input:"Input"},_={engine:"Engine",language:"Language",voice:"Voice",tts_input:"Input"},g={ready:0,wake_word:1,stt:2,intent:3,tts:4,done:5,error:6},v=(e,t)=>e.init_options?g[e.init_options.start_stage]<=g[t]&&g[t]<=g[e.init_options.end_stage]:t in e,m=(e,t,i)=>"error"in e&&i===t?s.dy`
    <ha-alert alert-type="error">
      ${e.error.message} (${e.error.code})
    </ha-alert>
  `:"",y=(e,t,i,a="-start")=>{const o=t.events.find((e=>e.type===`${i}`+a)),n=t.events.find((e=>e.type===`${i}-end`));if(!o)return"";if(!n)return"error"in t?s.dy`❌`:s.dy` <ha-spinner size="small"></ha-spinner> `;const d=new Date(n.timestamp).getTime()-new Date(o.timestamp).getTime(),l=(0,r.uf)(d/1e3,e.locale,{maximumFractionDigits:2});return s.dy`${l}s ✅`},f=(e,t)=>Object.entries(t).map((([t,i])=>s.dy`
      <div class="row">
        <div>${i}</div>
        <div>${e[t]}</div>
      </div>
    `)),b=(e,t)=>{const i={};let a=!1;for(const s in e)s in t||"done"===s||(a=!0,i[s]=e[s]);return a?s.dy`<ha-expansion-panel>
        <span slot="header">Raw</span>
        <ha-yaml-editor readOnly autoUpdate .value=${i}></ha-yaml-editor>
      </ha-expansion-panel>`:""};class w extends s.oi{render(){const e=this.pipelineRun&&["tts","intent","stt","wake_word"].find((e=>e in this.pipelineRun))||"ready",t=[],i=(this.pipelineRun.init_options&&"text"in this.pipelineRun.init_options.input?this.pipelineRun.init_options.input.text:void 0)||this.pipelineRun?.stt?.stt_output?.text||this.pipelineRun?.intent?.intent_input;return i&&t.push({from:"user",text:i}),this.pipelineRun?.intent?.intent_output?.response?.speech?.plain?.speech&&t.push({from:"hass",text:this.pipelineRun.intent.intent_output.response.speech.plain.speech}),s.dy`
      <ha-card>
        <div class="card-content">
          <div class="row heading">
            <div>Run</div>
            <div>${this.pipelineRun.stage}</div>
          </div>

          ${f(this.pipelineRun.run,p)}
          ${t.length>0?s.dy`
                <div class="messages">
                  ${t.map((({from:e,text:t})=>s.dy`
                      <div class=${`message ${e}`}>${t}</div>
                    `))}
                </div>
                <div style="clear:both"></div>
              `:""}
        </div>
      </ha-card>

      ${m(this.pipelineRun,"ready",e)}
      ${v(this.pipelineRun,"wake_word")?s.dy`
            <ha-card>
              <div class="card-content">
                <div class="row heading">
                  <span>Wake word</span>
                  ${y(this.hass,this.pipelineRun,"wake_word")}
                </div>
                ${this.pipelineRun.wake_word?s.dy`
                      <div class="card-content">
                        ${f(this.pipelineRun.wake_word,c)}
                        ${this.pipelineRun.wake_word.wake_word_output?s.dy`<div class="row">
                                <div>Model</div>
                                <div>
                                  ${this.pipelineRun.wake_word.wake_word_output.ww_id}
                                </div>
                              </div>
                              <div class="row">
                                <div>Timestamp</div>
                                <div>
                                  ${this.pipelineRun.wake_word.wake_word_output.timestamp}
                                </div>
                              </div>`:""}
                        ${b(this.pipelineRun.wake_word,h)}
                      </div>
                    `:""}
              </div>
            </ha-card>
          `:""}
      ${m(this.pipelineRun,"wake_word",e)}
      ${v(this.pipelineRun,"stt")?s.dy`
            <ha-card>
              <div class="card-content">
                <div class="row heading">
                  <span>Speech-to-text</span>
                  ${y(this.hass,this.pipelineRun,"stt","-vad-end")}
                </div>
                ${this.pipelineRun.stt?s.dy`
                      <div class="card-content">
                        ${f(this.pipelineRun.stt,c)}
                        <div class="row">
                          <div>Language</div>
                          <div>${this.pipelineRun.stt.metadata.language}</div>
                        </div>
                        ${this.pipelineRun.stt.stt_output?s.dy`<div class="row">
                              <div>Output</div>
                              <div>${this.pipelineRun.stt.stt_output.text}</div>
                            </div>`:""}
                        ${b(this.pipelineRun.stt,c)}
                      </div>
                    `:""}
              </div>
            </ha-card>
          `:""}
      ${m(this.pipelineRun,"stt",e)}
      ${v(this.pipelineRun,"intent")?s.dy`
            <ha-card>
              <div class="card-content">
                <div class="row heading">
                  <span>Natural Language Processing</span>
                  ${y(this.hass,this.pipelineRun,"intent")}
                </div>
                ${this.pipelineRun.intent?s.dy`
                      <div class="card-content">
                        ${f(this.pipelineRun.intent,u)}
                        ${this.pipelineRun.intent.intent_output?s.dy`<div class="row">
                                <div>Response type</div>
                                <div>
                                  ${this.pipelineRun.intent.intent_output.response.response_type}
                                </div>
                              </div>
                              ${"error"===this.pipelineRun.intent.intent_output.response.response_type?s.dy`<div class="row">
                                    <div>Error code</div>
                                    <div>
                                      ${this.pipelineRun.intent.intent_output.response.data.code}
                                    </div>
                                  </div>`:""}`:""}
                        <div class="row">
                          <div>Prefer handling locally</div>
                          <div>
                            ${this.pipelineRun.intent.prefer_local_intents}
                          </div>
                        </div>
                        <div class="row">
                          <div>Processed locally</div>
                          <div>
                            ${this.pipelineRun.intent.processed_locally}
                          </div>
                        </div>
                        ${b(this.pipelineRun.intent,u)}
                      </div>
                    `:""}
              </div>
            </ha-card>
          `:""}
      ${m(this.pipelineRun,"intent",e)}
      ${v(this.pipelineRun,"tts")?s.dy`
            <ha-card>
              <div class="card-content">
                <div class="row heading">
                  <span>Text-to-speech</span>
                  ${y(this.hass,this.pipelineRun,"tts")}
                </div>
                ${this.pipelineRun.tts?s.dy`
                      <div class="card-content">
                        ${f(this.pipelineRun.tts,_)}
                        ${b(this.pipelineRun.tts,_)}
                      </div>
                    `:""}
              </div>
              ${this.pipelineRun?.tts?.tts_output?s.dy`
                    <div class="card-actions">
                      <ha-button @click=${this._playTTS}>
                        Play Audio
                      </ha-button>
                    </div>
                  `:""}
            </ha-card>
          `:""}
      ${m(this.pipelineRun,"tts",e)}
      <ha-card>
        <ha-expansion-panel>
          <span slot="header">Raw</span>
          <ha-yaml-editor
            read-only
            auto-update
            .value=${this.pipelineRun}
          ></ha-yaml-editor>
        </ha-expansion-panel>
      </ha-card>
    `}_playTTS(){const e=this.pipelineRun.tts.tts_output.url,t=new Audio(e);t.addEventListener("error",(()=>{(0,d.Ys)(this,{title:"Error",text:"Error playing audio"})})),t.addEventListener("canplaythrough",(()=>{t.play()}))}}w.styles=s.iv`
    :host {
      display: block;
    }
    ha-card,
    ha-alert {
      display: block;
      margin-bottom: 16px;
    }
    .row {
      display: flex;
      justify-content: space-between;
    }
    .row > div:last-child {
      text-align: right;
    }
    ha-expansion-panel {
      padding-left: 8px;
      padding-inline-start: 8px;
      padding-inline-end: initial;
    }
    .card-content ha-expansion-panel {
      padding-left: 0px;
      padding-inline-start: 0px;
      padding-inline-end: initial;
      --expansion-panel-summary-padding: 0px;
      --expansion-panel-content-padding: 0px;
    }
    .heading {
      font-weight: var(--ha-font-weight-medium);
      margin-bottom: 16px;
    }

    .messages {
      margin-top: 8px;
    }

    .message {
      font-size: var(--ha-font-size-l);
      margin: 8px 0;
      padding: 8px;
      border-radius: 15px;
      clear: both;
    }

    .message.user {
      margin-left: 24px;
      margin-inline-start: 24px;
      margin-inline-end: initial;
      float: var(--float-end);
      text-align: right;
      border-bottom-right-radius: 0px;
      background-color: var(--light-primary-color);
      color: var(--text-light-primary-color, var(--primary-text-color));
      direction: var(--direction);
    }

    .message.hass {
      margin-right: 24px;
      margin-inline-end: 24px;
      margin-inline-start: initial;
      float: var(--float-start);
      border-bottom-left-radius: 0px;
      background-color: var(--primary-color);
      color: var(--text-primary-color);
      direction: var(--direction);
    }
  `,(0,a.__decorate)([(0,o.Cb)({attribute:!1})],w.prototype,"hass",void 0),(0,a.__decorate)([(0,o.Cb)({attribute:!1})],w.prototype,"pipelineRun",void 0),w=(0,a.__decorate)([(0,o.Mo)("assist-render-pipeline-run")],w),t()}catch(p){t(p)}}))},44062:function(e,t,i){i.a(e,(async function(e,a){try{i.r(t),i.d(t,{DialogVoiceAssistantPipelineDetail:()=>m});var s=i(73742),o=i(59048),n=i(7616),r=i(28105),d=i(29740),l=i(41806),p=i(76151),h=(i(30337),i(76528),i(91337),i(93795),i(32518)),c=i(77204),u=(i(10929),i(44618),i(11011),i(2994),i(7235),i(30227)),_=e([u]);u=(_.then?(await _)():_)[0];const g="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",v="M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z";class m extends o.oi{showDialog(e){if(this._params=e,this._error=void 0,this._cloudActive=this._params.cloudActiveSubscription,this._params.pipeline)return this._data={prefer_local_intents:!1,...this._params.pipeline},void(this._hideWakeWord=this._params.hideWakeWord||!this._data.wake_word_entity);let t,i;if(this._hideWakeWord=!0,this._cloudActive)for(const a of Object.values(this.hass.entities))if("cloud"===a.platform)if("stt"===(0,p.M)(a.entity_id)){if(t=a.entity_id,i)break}else if("tts"===(0,p.M)(a.entity_id)&&(i=a.entity_id,t))break;this._data={language:(this.hass.config.language||this.hass.locale.language).substring(0,2),stt_engine:t,tts_engine:i}}closeDialog(){this._params=void 0,this._data=void 0,this._hideWakeWord=!1,(0,d.B)(this,"dialog-closed",{dialog:this.localName})}firstUpdated(){this._getSupportedLanguages()}async _getSupportedLanguages(){const{languages:e}=await(0,h.fetchAssistPipelineLanguages)(this.hass);this._supportedLanguages=e}render(){if(!this._params||!this._data)return o.Ld;const e=this._params.pipeline?.id?this._params.pipeline.name:this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.add_assistant_title");return o.dy`
      <ha-dialog
        open
        @closed=${this.closeDialog}
        scrimClickAction
        escapeKeyAction
        .heading=${e}
      >
        <ha-dialog-header slot="heading">
          <ha-icon-button
            slot="navigationIcon"
            dialogAction="cancel"
            .label=${this.hass.localize("ui.common.close")}
            .path=${g}
          ></ha-icon-button>
          <span slot="title" .title=${e}>${e}</span>
          ${this._hideWakeWord&&!this._params.hideWakeWord&&this._hasWakeWorkEntities(this.hass.states)?o.dy`<ha-button-menu
                slot="actionItems"
                @action=${this._handleShowWakeWord}
                @closed=${l.U}
                menu-corner="END"
                corner="BOTTOM_END"
              >
                <ha-icon-button
                  .path=${v}
                  slot="trigger"
                ></ha-icon-button>
                <ha-list-item>
                  ${this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.add_streaming_wake_word")}
                </ha-list-item></ha-button-menu
              >`:o.Ld}
        </ha-dialog-header>
        <div class="content">
          ${this._error?o.dy`<ha-alert alert-type="error">${this._error}</ha-alert>`:o.Ld}
          <assist-pipeline-detail-config
            .hass=${this.hass}
            .data=${this._data}
            .supportedLanguages=${this._supportedLanguages}
            keys="name,language"
            @value-changed=${this._valueChanged}
            ?dialogInitialFocus=${!this._params.pipeline?.id}
          ></assist-pipeline-detail-config>
          <assist-pipeline-detail-conversation
            .hass=${this.hass}
            .data=${this._data}
            keys="conversation_engine,conversation_language,prefer_local_intents"
            @value-changed=${this._valueChanged}
          ></assist-pipeline-detail-conversation>
          ${this._cloudActive||"cloud"!==this._data.tts_engine&&"cloud"!==this._data.stt_engine?o.Ld:o.dy`
                <ha-alert alert-type="warning">
                  ${this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.no_cloud_message")}
                  <a href="/config/cloud" slot="action">
                    <ha-button>
                      ${this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.no_cloud_action")}
                    </ha-button>
                  </a>
                </ha-alert>
              `}
          <assist-pipeline-detail-stt
            .hass=${this.hass}
            .data=${this._data}
            keys="stt_engine,stt_language"
            @value-changed=${this._valueChanged}
          ></assist-pipeline-detail-stt>
          <assist-pipeline-detail-tts
            .hass=${this.hass}
            .data=${this._data}
            keys="tts_engine,tts_language,tts_voice"
            @value-changed=${this._valueChanged}
          ></assist-pipeline-detail-tts>
          ${this._hideWakeWord?o.Ld:o.dy`<assist-pipeline-detail-wakeword
                .hass=${this.hass}
                .data=${this._data}
                keys="wake_word_entity,wake_word_id"
                @value-changed=${this._valueChanged}
              ></assist-pipeline-detail-wakeword>`}
        </div>
        <ha-button
          slot="primaryAction"
          @click=${this._updatePipeline}
          .disabled=${this._submitting}
          dialogInitialFocus
        >
          ${this._params.pipeline?.id?this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.update_assistant_action"):this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.add_assistant_action")}
        </ha-button>
      </ha-dialog>
    `}_handleShowWakeWord(){this._hideWakeWord=!1}_valueChanged(e){this._error=void 0;const t={};e.currentTarget.getAttribute("keys").split(",").forEach((i=>{t[i]=e.detail.value[i]})),this._data={...this._data,...t}}async _updatePipeline(){this._submitting=!0;try{const e=this._data,t={name:e.name,language:e.language,conversation_engine:e.conversation_engine,conversation_language:e.conversation_language??null,prefer_local_intents:e.prefer_local_intents??!0,stt_engine:e.stt_engine??null,stt_language:e.stt_language??null,tts_engine:e.tts_engine??null,tts_language:e.tts_language??null,tts_voice:e.tts_voice??null,wake_word_entity:e.wake_word_entity??null,wake_word_id:e.wake_word_id??null};this._params.pipeline?.id?await this._params.updatePipeline(t):this._params.createPipeline?await this._params.createPipeline(t):console.error("No createPipeline function provided"),this.closeDialog()}catch(e){this._error=e?.message||"Unknown error"}finally{this._submitting=!1}}static get styles(){return[c.yu,o.iv`
        .content > *:not(:last-child) {
          margin-bottom: 16px;
          display: block;
        }
        ha-alert {
          margin-bottom: 16px;
          display: block;
        }
        a {
          text-decoration: none;
        }
      `]}constructor(...e){super(...e),this._hideWakeWord=!1,this._submitting=!1,this._hasWakeWorkEntities=(0,r.Z)((e=>Object.keys(e).some((e=>e.startsWith("wake_word.")))))}}(0,s.__decorate)([(0,n.Cb)({attribute:!1})],m.prototype,"hass",void 0),(0,s.__decorate)([(0,n.SB)()],m.prototype,"_params",void 0),(0,s.__decorate)([(0,n.SB)()],m.prototype,"_data",void 0),(0,s.__decorate)([(0,n.SB)()],m.prototype,"_hideWakeWord",void 0),(0,s.__decorate)([(0,n.SB)()],m.prototype,"_cloudActive",void 0),(0,s.__decorate)([(0,n.SB)()],m.prototype,"_error",void 0),(0,s.__decorate)([(0,n.SB)()],m.prototype,"_submitting",void 0),(0,s.__decorate)([(0,n.SB)()],m.prototype,"_supportedLanguages",void 0),m=(0,s.__decorate)([(0,n.Mo)("dialog-voice-assistant-pipeline-detail")],m),a()}catch(g){a(g)}}))}};
//# sourceMappingURL=1705.0ab86f01ca96e446.js.map