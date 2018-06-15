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
import 'rxjs/add/observable/interval';
import 'rxjs/add/operator/do';
import 'rxjs/add/operator/map';
import { TranslateService } from "@ngx-translate/core";
import { NgbModal, ModalDismissReasons } from "@ng-bootstrap/ng-bootstrap";
import { CommonService } from "@geonature_common/service/common.service";
import { DynamicFormComponent } from "@geonature_common/form/dynamic-form/dynamic-form.component";
import { DynamicFormService } from "@geonature_common/form/dynamic-form/dynamic-form.service";
import { Export, ExportService } from "../services/export.service";



@Component({
  selector: 'ng-pbar',
  template: `<p><ngb-progressbar type="info" [value]="completion.percent | async" [striped]="true" [animated]="true"></ngb-progressbar></p>`
})
export class NgPBar {
  completion = {
    percent: Observable.interval(200).map(val => val % 100).do(val => console.log(val))
  }
}


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
  public today = Date.now();
  public barHide: boolean = false;
  public closeResult: string;
  @ViewChild(NgbModal)
  // @ViewChild(NgPBar)
  constructor(
    private store: ExportService,
    private _commonService: CommonService,
    private _translate: TranslateService,
    private _router: Router,
    private modalService: NgbModal,
    private _fb: FormBuilder,
    private _dynformService: DynamicFormService) {

    this.modalForm = this._fb.group({
      adresseMail:['', Validators.compose([Validators.required, Validators.email])],
      chooseFormat:['', Validators.required],
      chooseStandard:['', Validators.required]
    });

    this.exports$ = this.store.exports;
    this.store.getExports();
  }

  get chooseFormat() {
    return this.modalForm.get('chooseFormat');
  }

  get chooseStandard() {
    return this.modalForm.get('chooseStandard');
  }

  //Fonction pour envoyer un mail à l'utilisateur lorsque le ddl est terminé.
  get adresseMail() {
    return this.modalForm.get('adresseMail');
  }

  open(content) {
    this.modalService.open(content).result.then((result) => {
      this.closeResult = `Closed with: ${result}`;
    }, (reason) => {
      this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
    });
  }

  private getDismissReason(reason: any): string {
    if (reason === ModalDismissReasons.ESC) {
      return 'by pressing ESC';
    } else if (reason === ModalDismissReasons.BACKDROP_CLICK) {
      return 'by clicking on a backdrop';
    } else {
      return  `with: ${reason}`;
    }
  }
  //Fonction qui bloque le boutton de validation tant que la licence n'est pas checkée
  follow() {
    this.buttonDisabled = !this.buttonDisabled;
    // this.showme()
  }

  //Fonction qui affiche la barre de téléchargement après validation
  showme() {
    this.barHide = !this.barHide;

    var choice = window.document.querySelector('input[name="options"]:checked');

    console.log('format:', this.chooseFormat.value)
    console.log('export_id:', choice.id)
    this.store.downloadExport(parseFloat(choice.id))
  }

  //Fonction pour avoir un modal vierge si l'on ferme puis réouvre le modal
  resetModal() {
    this.modalForm.reset();
  }

}
