import { 
  testAuditYearCheckbox,
  testUEIorEin,
  testALN,
  testName,
  testFACacceptanceDate,
  testState,
  testCogorOver,
  testAuditFindings,
  testDirectFunding,
  testMajorProgram
} from '../support/search-audit-reports.js';

    // describe('Test Search Page', () => {
    //     it('Display the search page', () => {
    //       testSearch();
    //     });
    //   });

      // describe('Test Audit Year Checkbox', () => {
      //   it('checks Audit Years', () => {
      //     testAuditYearCheckbox();
      //   });
      // });

      describe('Test UEI or EIN Field', () => {
        it('checks UEI or EIN', () => {
          testUEIorEin();
        });
      });

      describe('Test ALN(CFDA) Field', () => {
        it('checks ALN', () => {
          testALN();
        });
      });

      describe('Test Name Field', () => {
        it('checks Name of Entity, Auditee, or Auditor', () => {
          testName();
        });
      });

      describe('Test FAC Acceptance Date Field', () => {
        it('checks FAC acceptance date', () => {
          testFACacceptanceDate();
        });
      });

      describe('Test State Field', () => {
        it('checks State', () => {
          testState();
        });
      });

      describe('Test Cog or Over Field', () => {
        it('checks Cog or Over', () => {
          testCogorOver();
        });
      });

      describe('Test Audit Findings Field', () => {
        it('checks Audit Findings', () => {
          testAuditFindings();
        });
      });

      describe('Test Direct Funding Field', () => {
        it('checks Direct Funding', () => {
          testDirectFunding();
        });
      });

      describe('Test Major Program Field', () => {
        it('checks Major Program', () => {
          testMajorProgram();
        });
      });


      