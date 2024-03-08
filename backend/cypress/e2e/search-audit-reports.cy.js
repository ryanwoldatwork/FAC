import searchPage from '../pageObjects/searchPage.js';

let search;

beforeEach(() => {
  cy.visit('/dissemination/search/');
  search = new searchPage();
});

      describe('Test Audit Year Checkbox', () => {
        it('checks Audit Years', () => {
          search.checkAuditYearCheckbox('2023');
          search.uncheckAuditYearCheckbox('2023');
          const yearsToCheck = ['all_years','2023','2022','2021','2020','2019','2018','2017','2016'];
          yearsToCheck.forEach((year) => {
            search.checkAuditYearCheckbox(year);
          });
          yearsToCheck.forEach((year) => {
            search.uncheckAuditYearCheckbox(year);
          })
        });
      });

      describe('Test UEI or EIN Field', () => {
        it('checks UEI or EIN', () => {
          search.testUEIorEin('D7A4J33FUMJ1');
        });
      });

      describe('Test ALN(CFDA) Field', () => {
        it('checks ALN', () => {
          search.testALN('93');
        });
      });

      describe('Test Name Field', () => {
        it('checks Name of Entity, Auditee, or Auditor', () => {
          search.testName('Audit McAuditee');
        });
      });

      describe('Test FAC Acceptance Date Field', () => {
        it('checks FAC acceptance date', () => {
          search.testFACacceptanceDate('03/01/2024', '03/31/2024');
        });
      });

      describe('Test State Field', () => {
        it('checks State', () => {
          search.testState('VA');
        });
      });

      describe('Test Cog or Over Field', () => {
        it('checks Cog or Over', () => {
          search.testCogorOver('oversight');
        });
      });

      describe('Test Audit Findings Checkbox', () => {
        it('checks Audit Findings', () => {
          search.openFindingsAccordion();
          const auditFindingsCheckbox = ['all_findings', 'is_modified_opinion', 'is_other_findings', 'is_material_weakness', 'is_significant_deficiency', 'is_other_matters', 'is_questioned_costs', 'is_repeat_finding'];
          auditFindingsCheckbox.forEach((findings) => {
            search.checkAuditFindingsCheckbox(findings);
          });
          auditFindingsCheckbox.forEach((findings) => {
            search.uncheckAuditFindingsCheckbox(findings);
          })
        });
      });

      describe('Test Direct Funding Field', () => {
        it('checks Direct Funding', () => {
          search.openDirectFundingAccordion();
          const directFundingCheckbox = ['direct_funding', 'passthrough_funding'];
          directFundingCheckbox.forEach((funding) => {
            search.checkDirectFundingCheckbox(funding);
          });
          directFundingCheckbox.forEach((funding) => {
            search.uncheckDirectFundingCheckbox(funding);
          });
        });
      });

      describe('Test Major Program Field', () => {
        it('checks Major Program', () => {
          search.openMajorProgramAccordion();
          search.checkMajorProgramRadio('True');
          search.uncheckMajorProgramRadio('False');
        });
      });

      // describe('Test Search Submit', () => {
      //   it('clicks Search Submit Button', () => {
      //     search.testSearchSubmitButton();
      //   });
      // });


      