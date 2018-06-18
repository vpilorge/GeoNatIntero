import { Injectable } from "@angular/core";
import {
  HttpClient,
  HttpEvent,
  HttpHeaders,
  HttpRequest,
  HttpEventType,
  HttpErrorResponse
} from "@angular/common/http";
import { Observable } from "rxjs/Observable";
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { share } from 'rxjs/operators/share';
import { map } from "rxjs/operator/map";
import 'rxjs/add/observable/interval';
import 'rxjs/add/operator/takeWhile';

import { AppConfig } from "@geonature_config/app.config";
import { filter } from "rxjs/operator/filter";


export interface Export {
  label: string;
  id: string;
  date: Date;
  standard: string;
  selection: string;
  extension: string;
}

const apiEndpoint='http://localhost:8000/interop';

@Injectable()
export class ExportService {
  exports: BehaviorSubject<Export[]>
  labels: BehaviorSubject<string[]>
  private _blob: Blob = null

  constructor(private _api: HttpClient) {
    this.exports = <BehaviorSubject<Export[]>>new BehaviorSubject([]);
    this.labels = <BehaviorSubject<string[]>>new BehaviorSubject([]);
  }

  getExports() {
    this._api.get(`${apiEndpoint}/exports`).subscribe(
      (exports: Export[]) => {
        console.debug('exports:', exports)
        this.exports.next(exports);
      },
      error => console.error(error),
      () => {
        console.log(`getExports(): ${this.exports.value.length} exports`)
        this.getLabels()
      }
    )
  }

  getLabels() {
    let labels = []
    this.exports.subscribe(val => val.map((x) => labels.push({'label': x.label, 'date': x.date})))
      let seen = new Set()
      let uniqueLabels = labels.filter(item => {
        let k = item.label
        return seen.has(k) ? false : seen.add(k)
      })
    this.labels.next(uniqueLabels)
  }

  getExport(label, standard, extension) {
    console.debug(label, standard, extension)
    let source = this.exports.map(
      (exports: Export[]) => exports.filter(
          (x: Export) => x.label == label && x.standard == standard && x.extension == extension)  // FIXME: csv
      )

    let subscription = source.subscribe(
      x => {
        // debugger;  // FIXME: csv
        // console.log(x, x[0].id)
        console.log(x)
        this.downloadExport(parseFloat(x[0].id), x[0].standard, x[0].extension)
      },
      e => console.log(e.message),
      () => console.log('completed')
    )
  }

  downloadExport(submissionID: number, standard: string, ext: string) {
    const url = `${apiEndpoint}/exports/export_${standard}_${submissionID}.${ext}`
    console.log(url)
    // window.open(url)
    this._api.get(url, {
      headers: new HttpHeaders().set('Content-Type', `text/${ext}`),  // FIXME: Mime
      observe: 'events',
      responseType: 'blob',
      reportProgress: true,
    }).subscribe(
      event => {
        if (event.type === HttpEventType.DownloadProgress) {
            if (event.hasOwnProperty('total')) {
              const percentage = 100 / event.total * event.loaded;
              console.log(`Downloaded ${percentage}%.`);
            } else {
              let kbLoaded = Math.round(event.loaded / 1024);
              console.log(`Downloaded ${kbLoaded}Kb.`);
            }
        }
        if (event.type === HttpEventType.Response) {
          console.log('API content-type', event.headers.get("Content-Type"))
          this._blob = new Blob([event.body], {type: event.headers.get("Content-Type")});
        }
      },
      (err: HttpErrorResponse) => {
        console.log(err.error);
        console.log(err.name);
        console.log(err.message);
        console.log(err.status);
      },
      () => {
        let link = document.createElement("a")
        link.href = URL.createObjectURL(this._blob)
        link.setAttribute('visibility','hidden')
        link.download = `${submissionID}.${ext}`
        link.onload = function() { URL.revokeObjectURL(link.href) }
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      }
    );
  }


  /*
  getExportProgress(submissionID: number, ext='csv') {
    let progress = Observable.interval(1500)
      .switchMap(() => this._api.get(`${apiEndpoint}/progress/${submissionID}`))
      .map(data => data.json())
      .takeWhile(data => data.status === '-2')
      .subscribe(
        data => {
          // progress feedback:
          // https://www.postgresql.org/message-id/CADdR5ny_0dFwnD%2BsuBnV1Vz6NDKbFHeWoV1EDv9buhDCtc3aAA%40mail.gmail.com
          console.debug(data)
        },
        error => console.error(error),
        () => {
          progress.unsubscribe();
          window.open(`${apiEndpoint}/exports/export_${submissionID}.${data.format}`);
        });
  }
  */
}
