export type Raw=Record<string,unknown>&{_key:string};
export interface Career{key:string;id:string;name:string;description:string;careerGroup:string;iscoGroup:string;escoUri:string}
export interface Skill{key:string;id:string;name:string;description:string;skillType:string;escoUri:string;reuseLevel:string|null}
export interface SkillGroup{key:string;id:string;name:string;description:string;code:string;escoUri:string}
export interface Course{key:string;id:string;title:string;canonicalUrl:string;providerName:string;resourceType:string;language:string;level:string|null;certificateAvailable:boolean|null;verifiedOutcomeProficiency:string|null;raw:Raw}
export interface Provider{key:string;id:string;name:string;officialWebsite:string|null}
export interface Edge{key:string;id:string;from:string;to:string;raw:Raw}
export interface Requirement extends Edge{requirementType:'essential'|'optional';requiredLevel:null;skill:Skill;resourceCount:number}
export interface Evidence{edge:Edge;evidenceScope:'direct_topic'|'partial';evidenceLimit:string|null}
export interface GraphData{nodes:Array<{id:string;type:string;label:string}>;edges:Array<{id:string;source:string;target:string;type:string;data?:any}>}
export interface CatalogPayload{release:{version:string;sprint:number;records:number};handoff:Record<string,unknown>;manifest:Record<string,unknown>;collections:Record<string,Raw[]>;reports:{coverage:string;gaps:string;legacyAudit:string}}
