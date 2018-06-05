import {
  Component,
  Renderer2,
  ViewChild,
  Pipe,
  PipeTransform
} from "@angular/core";
import { DatePipe } from '@angular/common';
import {
  FormControl,
  FormGroup,
  FormBuilder,
  FormsModule,
  ReactiveFormsModule,
  Validators
} from "@angular/forms";
import { Router } from "@angular/router";
import { Observable } from "rxjs/Observable";
import { TranslateService } from "@ngx-translate/core";
import { NgbModal, ModalDismissReasons } from "@ng-bootstrap/ng-bootstrap";
import { CommonService } from "@geonature_common/service/common.service";
import { DynamicFormComponent } from "@geonature_common/form/dynamic-form/dynamic-form.component";
import { DynamicFormService } from "@geonature_common/form/dynamic-form/dynamic-form.service";
import { Export, ExportService } from "../services/export.service";


@Component({
  selector: "pnx-export-map-list",
  templateUrl: "export-map-list.component.html",
  styleUrls: ["./export-map-list.component.scss"],
  providers: []
})
export class ExportMapListComponent {
  exports$: Observable<Export[]>
  public modalForm : FormGroup;
  public buttonDisabled: boolean = false;
  public barHide: boolean = false;
  public today = Date.now();
  @ViewChild(NgbModal) public modalCol: NgbModal;
  constructor(
    private store: ExportService,
    private _commonService: CommonService,
    private _translate: TranslateService,
    private _router: Router,
    public ngbModal: NgbModal,
    private _fb: FormBuilder,
    private _dynformService: DynamicFormService) {

    this.modalForm = this._fb.group({
      adresseMail:['', Validators.compose([Validators.required, Validators.email])]
    });
    this.exports$ = this.store.exports;
    this.store.getExports();
  }

  //Fonction qui bloque le boutton de validation tant que la licence n'est pas checkée
  follow() {
    this.buttonDisabled = !this.buttonDisabled;
  }

  //Fonction qui affiche la barre de téléchargement après validation
  showme() {
    this.barHide = !this.barHide;
    const exportList = window.document.querySelectorAll('input[name="options"]:checked');
    const submissionID = /export_(\d+\.\d+)\.csv/.exec(exportList[0].id)[1]
    this.store.downloadExport(parseFloat(submissionID))
  }

  //Fonction pour avoir un modal vierge si l'on ferme puis réouvre le modal
  resetModal() {
    this.modalForm.reset();
  }

  //Fonction pour envoyer un mail à l'utilisateur lorsque le ddl est terminé.
  get adresseMail() { return this.modalForm.get('adresseMail'); }

}
