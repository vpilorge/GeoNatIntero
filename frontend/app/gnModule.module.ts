import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { Routes, RouterModule } from "@angular/router";
import { HttpClientModule } from "@angular/common/http";
import { GN2CommonModule } from "@geonature_common/GN2Common.module";
import { TranslateHttpLoader } from "@ngx-translate/http-loader";
import { ExportMapListComponent } from "./export-map-list/export-map-list.component";
import { ExportService } from "./services/export.service";

const routes: Routes = [
  { path: "", component: ExportMapListComponent }
];

@NgModule({
  imports: [
    HttpClientModule,
    CommonModule,
    GN2CommonModule,
    RouterModule.forChild(routes)
  ],
  declarations: [
    ExportMapListComponent
  ],
  providers: [
    ExportService
  ],
  bootstrap: []
})
export class GeonatureModule {}
