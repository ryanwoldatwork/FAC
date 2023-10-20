import { testCrossValidation } from './cross-validation.js';
import { testLoginGovLogin } from './login-gov.js';
import { testLogoutGov } from './logout-gov.js';
import { testValidAccess } from './check-access.js';
import { testValidEligibility } from './check-eligibility.js';
import { testValidAuditeeInfo } from './auditee-info.js';
import { testValidGeneralInfo } from './general-info.js';
import { testAuditInformationForm } from './audit-info-form.js';
import { testPdfAuditReport } from './report-pdf.js';
import { testAuditorCertification } from './auditor-certification.js';
import { testAuditeeCertification } from './auditee-certification.js';
import { testReportIdFound, testReportIdNotFound } from './dissemination-table.js';
import { testTribalAuditPublic, testTribalAuditPrivate } from './tribal-audit-form.js';

import {
  testWorkbookFederalAwards,
  testWorkbookNotesToSEFA,
  testWorkbookFindingsUniformGuidance,
  testWorkbookFindingsText,
  testWorkbookCorrectiveActionPlan,
  testWorkbookAdditionalUEIs,
  testWorkbookSecondaryAuditors,
  testWorkbookAdditionalEINs
} from './workbook-uploads.js';

const LOGIN_TEST_EMAIL_AUDITEE = Cypress.env('LOGIN_TEST_EMAIL_AUDITEE');
const LOGIN_TEST_PASSWORD_AUDITEE = Cypress.env('LOGIN_TEST_PASSWORD_AUDITEE');
const LOGIN_TEST_OTP_SECRET_AUDITEE = Cypress.env('LOGIN_TEST_OTP_SECRET_AUDITEE');

export function testFullSubmission(isTribal, isPublic) {
  cy.visit('/');
  cy.url().should('include', '/');

  // Logs in with Login.gov'
  testLoginGovLogin();

  // Moves on to the eligibility screen
  // check the terms and conditions link and click "Accept and start..."
  //
  // this click actually goes to the "terms and conditions" link which
  // brings up a modal
  cy.get('label[for=check-start-new-submission]').click();
  cy.get('.usa-button').contains('Accept and start').click();
  cy.url().should('match', /\/report_submission\/eligibility\/$/);

  // Completes the eligibility screen
  testValidEligibility(isTribal);

  // Now the auditee info screen
  testValidAuditeeInfo();

  // Now the accessandsubmission screen
  testValidAccess();

  // Report should not yet be in the dissemination table
  cy.url().then(url => {
    const reportId = url.split('/').pop();
    testReportIdNotFound(reportId);
  });

  // Fill out the general info form
  testValidGeneralInfo();

  // Upload all the workbooks. Don't intercept the uploads, which means a file will make it into the DB.
  cy.get(".usa-link").contains("Federal Awards").click();
  testWorkbookFederalAwards(false);

  cy.get(".usa-link").contains("Notes to SEFA").click();
  testWorkbookNotesToSEFA(false);

  cy.get(".usa-link").contains("Audit report PDF").click();
  testPdfAuditReport(false);

  cy.get(".usa-link").contains("Federal Awards Audit Findings").click();
  testWorkbookFindingsUniformGuidance(false);

  cy.get(".usa-link").contains("Federal Awards Audit Findings Text").click();
  testWorkbookFindingsText(false);

  cy.get(".usa-link").contains("Corrective Action Plan").click();
  testWorkbookCorrectiveActionPlan(false);

  cy.get(".usa-link").contains("Additional UEIs").click();
  testWorkbookAdditionalUEIs(false);

  cy.get(".usa-link").contains("Secondary Auditors").click();
  testWorkbookSecondaryAuditors(false);

  cy.get(".usa-link").contains("Additional EINs").click();
  testWorkbookAdditionalEINs(false);

  if (isTribal) {
    cy.url().then(url => {
      const reportId = url.split('/').pop();

      // Complete the tribal audit form as auditee - opt private
      testLogoutGov();
      testLoginGovLogin(
        LOGIN_TEST_EMAIL_AUDITEE,
        LOGIN_TEST_PASSWORD_AUDITEE,
        LOGIN_TEST_OTP_SECRET_AUDITEE
      );
      cy.visit(`/audit/submission-progress/${reportId}`);
      cy.get(".usa-link").contains("Tribal data release").click();

      if (isPublic) {
        testTribalAuditPublic();
      } else {
        testTribalAuditPrivate();
      }

      // Login as Auditor
      testLogoutGov();
      testLoginGovLogin();
      cy.visit(`/audit/submission-progress/${reportId}`);
    })
  }

  // Complete the audit information form
  cy.get(".usa-link").contains("Audit Information form").click();
  testAuditInformationForm();

  cy.get(".usa-link").contains("Pre-submission validation").click();
  testCrossValidation();

  // Auditor certification
  cy.get(".usa-link").contains("Auditor Certification").click();
  testAuditorCertification();

  // Grab the report ID from the URL
  cy.url().then(url => {
    const reportId = url.split('/').pop();

    testLogoutGov();

    // Login as Auditee
    testLoginGovLogin(
      LOGIN_TEST_EMAIL_AUDITEE,
      LOGIN_TEST_PASSWORD_AUDITEE,
      LOGIN_TEST_OTP_SECRET_AUDITEE
    );

    cy.visit(`/audit/submission-progress/${reportId}`);

    // Auditee certification
    cy.get(".usa-link").contains("Auditee Certification").click();
    testAuditeeCertification();

    // Submit
    cy.get(".usa-link").contains("Submit to the FAC for processing").click();
    cy.url().should('match', /\/audit\/submission\/[0-9]{4}-[0-9]{2}-GSAFAC-[0-9]{10}/);
    cy.get('#continue').click();
    cy.url().should('match', /\/audit\//);

    // The report ID should be found in the Completed Audits table
    cy.get('.usa-table').contains(
      'caption',
      /audits are complete/
    ).siblings().contains('td', reportId);

    // The Report should not be in the dissemination table
    if (isPublic) {
      testReportIdFound(reportId);
    } else {
      testReportIdNotFound(reportId);
    }
  });

  testLogoutGov();
}