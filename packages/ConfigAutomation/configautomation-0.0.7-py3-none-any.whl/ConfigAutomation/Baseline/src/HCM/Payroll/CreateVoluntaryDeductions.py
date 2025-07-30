from playwright.sync_api import Playwright, sync_playwright, expect
from ConfigAutomation.Baseline.src.utils import *


def configure(playwright: Playwright, rowcount, datadict, videodir) -> dict:
    browser, context, page = OpenBrowser(playwright, False, videodir)
    page.goto(BASEURL)

    # Login to application
    page.wait_for_timeout(5000)
    if page.get_by_placeholder("User ID").is_visible():
        page.get_by_placeholder("User ID").click()
        page.get_by_placeholder("User ID").fill(IMPLUSRID)
        page.get_by_placeholder("Password").fill(IMPLUSRPWD)
    else:
        page.get_by_placeholder("User name").click()
        page.get_by_placeholder("User name").fill(IMPLUSRID)
        page.get_by_role("textbox", name="Password").fill(IMPLUSRPWD)
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_timeout(5000)

    # Navigate to Setup and Maintenance
    page.locator("//a[@title=\"Settings and Actions\"]").click()
    page.get_by_role("link", name="Setup and Maintenance").click()
    page.wait_for_timeout(40000)
    page.get_by_role("link", name="Tasks").click()

    # Entering respective option in global Search field and searching
    page.locator("[id=\"__af_Z_window\"]").get_by_role("link", name="Search").click()
    page.wait_for_timeout(3000)
    page.get_by_role("textbox").click()
    page.get_by_role("textbox").type("Elements")
    page.get_by_role("textbox").press("Enter")
    page.wait_for_timeout(2000)
    page.get_by_role("link", name="Elements", exact=True).click()

    i = 0
    while i < rowcount:
        datadictvalue = datadict[i]
        page.wait_for_timeout(10000)
        if page.locator("//a[text()='View']//following::div[@role='button'][1]").is_visible():
           page.locator("//a[text()='View']//following::div[@role='button'][1]").click()
        page.get_by_role("link", name="Create").click()
        page.locator("[id=\"__af_Z_window\"]").get_by_role("combobox", name="Legislative Data Group").click()
        page.wait_for_timeout(5000)
        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_LGSLTV_DATA_GROUP"], exact=True).click()
        page.wait_for_timeout(2000)
        page.get_by_role("combobox", name="Primary Classification").click()
        page.wait_for_timeout(3000)
        page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRMRY_CLSSFCTN"],exact=True).click()
        page.wait_for_timeout(2000)

        # Secondary Classification as Life Insurance
        if datadictvalue["C_SCNDRY_CLSSFCTN"]=='Life Insurance':
            page.get_by_role("combobox", name="Secondary Classification").click()
            page.wait_for_timeout(3000)
            page.get_by_text(datadictvalue["C_SCNDRY_CLSSFCTN"], exact=True).click()
            page.wait_for_timeout(2000)

            page.get_by_role("button", name="Continue").click()
            page.wait_for_timeout(3000)

            # Entering Basic Details
            page.get_by_label("Name", exact=True).type(datadictvalue["C_ELMNT_NAME"])
            page.get_by_label("Reporting Name").type(datadictvalue["C_RPRTNG_NAME"])
            page.get_by_label("Description").type(datadictvalue["C_DSCRPTN"])
            page.get_by_placeholder("m/d/yy").clear()
            page.get_by_placeholder("m/d/yy").type(datadictvalue["C_EFCTV_DATE"])

            # Selecting Currency
            page.get_by_role("combobox", name="Input Currency").click()
            page.wait_for_timeout(2000)
            page.get_by_text(datadictvalue["C_INPUT_CRNCY"],exact=True).click()

            # Selecting Duration
            if datadictvalue["C_ATMTC_ELMNT_ELGBLTY"] == 'Yes':
                page.locator("// label[text() = 'Should every person eligible for the element automatically receive it?'] // following::label[text() = 'Yes'][1]").click()
            else:
                page.locator("// label[text() = 'Should every person eligible for the element automatically receive it?'] // following::label[text() = 'No'][1]").click()

            page.wait_for_timeout(2000)
            page.get_by_role("combobox", name="What is the earliest entry").click()
            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_ERLST_ENTRY_DATE"]).click()
            page.get_by_role("combobox", name="What is the latest entry date").click()
            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_LTST_ENTRY_DATE"]).click()

            # Standard Rules

            ###Selecting At which employment level should this element be attached?
            if datadictvalue["C_EMPLYMNT_LEVEL_ELMNT"]=='Assignment Level':
                page.get_by_text("Assignment Level", exact=True).click()
            elif datadictvalue["C_EMPLYMNT_LEVEL_ELMNT"]=='Payroll relationship level':
                page.get_by_text("Payroll relationship level", exact=True).click()
            elif datadictvalue["C_EMPLYMNT_LEVEL_ELMNT"]=='Term Level':
                page.get_by_text("Term Level", exact=True).click()

            ### Does this element recur each payroll period, or does it require explicit entry?
            if datadictvalue["C_ELMNT_RCRRNG_NNRCRRNG"] == 'Recurring':
                page.get_by_text("Recurring", exact=True).click()
            else:
                page.get_by_text("Nonrecurring", exact=True).click()


            ### What should happen when there are insufficient funds to cover the deductions?
            if datadictvalue["C_INSFFCNT_PRTL_DDCTN"]=='Do not take a partial deduction or create arrears':
                page.get_by_text("Do not take a partial deduction or create arrears", exact=True).click()

            elif datadictvalue["C_INSFFCNT_PRTL_DDCTN"]=='Do not take partial deduction, place all in arrears':
                page.get_by_text("Do not take partial deduction, place all in arrears", exact=True).click()

            elif datadictvalue["C_INSFFCNT_PRTL_DDCTN"]=='Take a partial deduction, but do not create arrears':
                page.get_by_text("Take a partial deduction, but do not create arrears", exact=True).click()

            elif datadictvalue["C_INSFFCNT_PRTL_DDCTN"]=='Take a partial deduction, place remaining in arrears':
                page.get_by_text("Take a partial deduction, place remaining in arrears", exact=True).click()

            ### Selecting Process the element only once in each payroll period?
            if datadictvalue["C_PRCSS_ELMNT_ONLY_ONCE"] == 'Yes':
                page.locator("//label[text()='Process the element only once in each payroll period?']//following::label[text()='Yes'][1]").click()
            else:
                page.locator("//label[text()='Process the element only once in each payroll period?']//following::label[text()='No'][1]").click()

            ### Selecting Can a person have more than one entry of this element in a payroll period?
            if datadictvalue["C_MORE_THAN_ONE_ENTRY"] == 'Yes':
                page.locator("//label[text()='Can a person have more than one entry of this element in a payroll period?']//following::label[text()='Yes'][1]").click()
            else:
                page.locator("//label[text()='Can a person have more than one entry of this element in a payroll period?']//following::label[text()='No'][1]").click()

            ## Clicking on Next button
            page.get_by_role("button", name="Next").click()
            page.wait_for_timeout(3000)


            # Calculation Rules
            ### Based on Fixed amount deductions
            if datadictvalue["C_CLCLTN_RULE"]=='Fixed amount deduction':
                page.get_by_text("Fixed amount deduction", exact=True).click()

                # Special Rules
                ### Is this element subject to proration?
                if datadictvalue["C_ELMNT_PRRTN"]!='N/A':
                    if datadictvalue["C_ELMNT_PRRTN"]=='No':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='No'][1]").click()
                    elif datadictvalue["C_ELMNT_PRRTN"]=='Yes':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='Yes'][1]").click()
                        if datadictvalue["C_PRRTN_GROUP"]!='N/A':
                            page.wait_for_timeout(3000)
                            page.get_by_role("combobox", name="Proration Group").click()
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_GROUP"]).click()

                #### Is this element subject to retroactive changes?
                if datadictvalue["C_ELMNT_RTRCTV_CHNGS"]!='N/A':
                    if datadictvalue["C_ELMNT_RTRCTV_CHNGS"]=='No':
                        page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()
                    elif datadictvalue["C_ELMNT_RTRCTV_CHNGS"]=='Yes':
                        page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                        if datadictvalue["C_RETRO_GROUP"] != 'N/A':
                            page.wait_for_timeout(2000)
                            page.get_by_role("combobox", name="Retro Group").click()
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()

                #### Do you want to stop processing when the total owed is reached? If you enable total owed, a reference is required for each deduction entry.
                if datadictvalue["C_STOP_PRCSSNG"]!='N/A':
                    if datadictvalue["C_STOP_PRCSSNG"]=='No':
                        page.locator("//label[text()='Do you want to stop processing when the total owed is reached? If you enable total owed, a reference is required for each deduction entry.']//following::label[text()='No'][1]").click()
                    elif datadictvalue["C_STOP_PRCSSNG"]=='Yes':
                        page.locator("//label[text()='Do you want to stop processing when the total owed is reached? If you enable total owed, a reference is required for each deduction entry.']//following::label[text()='Yes'][1]").click()

            ### Based on Percentage deduction
            if datadictvalue["C_CLCLTN_RULE"]=='Percentage deduction':
                page.get_by_text("Percentage deduction", exact=True).click()

                # Special Rules
                ### Is this element subject to proration?
                if datadictvalue["C_ELMNT_PRRTN"]!='N/A':
                    if datadictvalue["C_ELMNT_PRRTN"]=='No':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='No'][1]").click()
                    elif datadictvalue["C_ELMNT_PRRTN"]=='Yes':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='Yes'][1]").click()
                        if datadictvalue["C_PRRTN_GROUP"]!='N/A':
                            page.wait_for_timeout(3000)
                            page.get_by_role("combobox", name="Proration Group").click()
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_GROUP"]).click()

                #### Is this element subject to retroactive changes?
                if datadictvalue["C_ELMNT_RTRCTV_CHNGS"]!='N/A':
                    if datadictvalue["C_ELMNT_RTRCTV_CHNGS"]=='No':
                        page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()
                    elif datadictvalue["C_ELMNT_RTRCTV_CHNGS"]=='Yes':
                        page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                        if datadictvalue["C_RETRO_GROUP"] != 'N/A':
                            page.wait_for_timeout(2000)
                            page.get_by_role("combobox", name="Retro Group").click()
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()

                #### Do you want to stop processing when the total owed is reached? If you enable total owed, a reference is required for each deduction entry.
                if datadictvalue["C_STOP_PRCSSNG"]!='N/A':
                    if datadictvalue["C_STOP_PRCSSNG"]=='No':
                        page.locator("//label[text()='Do you want to stop processing when the total owed is reached? If you enable total owed, a reference is required for each deduction entry.']//following::label[text()='No'][1]").click()
                    elif datadictvalue["C_STOP_PRCSSNG"]=='Yes':
                        page.locator("//label[text()='Do you want to stop processing when the total owed is reached? If you enable total owed, a reference is required for each deduction entry.']//following::label[text()='Yes'][1]").click()

        # Secondary Classification as Benefits After Tax
        if datadictvalue["C_SCNDRY_CLSSFCTN"] == 'Benefits After Tax':
            page.get_by_role("combobox", name="Secondary Classification").click()
            page.wait_for_timeout(3000)
            page.get_by_text(datadictvalue["C_SCNDRY_CLSSFCTN"], exact=True).click()
            page.wait_for_timeout(2000)

            page.get_by_role("button", name="Continue").click()
            page.wait_for_timeout(3000)

            # Entering Basic Details
            page.get_by_label("Name", exact=True).type(datadictvalue["C_ELMNT_NAME"])
            page.get_by_label("Reporting Name").type(datadictvalue["C_RPRTNG_NAME"])
            page.get_by_label("Description").type(datadictvalue["C_DSCRPTN"])
            page.get_by_placeholder("m/d/yy").clear()
            page.get_by_placeholder("m/d/yy").type(datadictvalue["C_EFCTV_DATE"])

            # Selecting Currency
            page.get_by_role("combobox", name="Input Currency").click()
            page.wait_for_timeout(2000)
            page.get_by_text(datadictvalue["C_INPUT_CRNCY"],exact=True).click()

            # Selecting Duration
            if datadictvalue["C_ATMTC_ELMNT_ELGBLTY"] == 'Yes':
                page.locator("// label[text() = 'Should every person eligible for the element automatically receive it?'] // following::label[text() = 'Yes'][1]").click()
            else:
                page.locator("// label[text() = 'Should every person eligible for the element automatically receive it?'] // following::label[text() = 'No'][1]").click()

            page.wait_for_timeout(2000)
            page.get_by_role("combobox", name="What is the earliest entry").click()
            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_ERLST_ENTRY_DATE"]).click()
            page.get_by_role("combobox", name="What is the latest entry date").click()
            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_LTST_ENTRY_DATE"]).click()

            # Standard Rules

            ###Selecting At which employment level should this element be attached?
            if datadictvalue["C_EMPLYMNT_LEVEL_ELMNT"] == 'Assignment Level':
                page.get_by_text("Assignment Level", exact=True).click()
            elif datadictvalue["C_EMPLYMNT_LEVEL_ELMNT"] == 'Payroll relationship level':
                page.get_by_text("Payroll relationship level", exact=True).click()
            elif datadictvalue["C_EMPLYMNT_LEVEL_ELMNT"] == 'Term Level':
                page.get_by_text("Term Level", exact=True).click()

            ### Does this element recur each payroll period, or does it require explicit entry?
            if datadictvalue["C_ELMNT_RCRRNG_NNRCRRNG"] == 'Recurring':
                page.get_by_text("Recurring", exact=True).click()
            else:
                page.get_by_text("Nonrecurring", exact=True).click()

            ### What should happen when there are insufficient funds to cover the deductions?
            if datadictvalue["C_INSFFCNT_PRTL_DDCTN"] == 'Do not take a partial deduction or create arrears':
                page.get_by_text("Do not take a partial deduction or create arrears", exact=True).click()

            elif datadictvalue[
                "C_INSFFCNT_PRTL_DDCTN"] == 'Do not take partial deduction, place all in arrears':
                page.get_by_text("Do not take partial deduction, place all in arrears", exact=True).click()

            elif datadictvalue[
                "C_INSFFCNT_PRTL_DDCTN"] == 'Take a partial deduction, but do not create arrears':
                page.get_by_text("Take a partial deduction, but do not create arrears", exact=True).click()

            elif datadictvalue[
                "C_INSFFCNT_PRTL_DDCTN"] == 'Take a partial deduction, place remaining in arrears':
                page.get_by_text("Take a partial deduction, place remaining in arrears", exact=True).click()

            ### Selecting Process the element only once in each payroll period?
            if datadictvalue["C_PRCSS_ELMNT_ONLY_ONCE"] == 'Yes':
                page.locator("//label[text()='Process the element only once in each payroll period?']//following::label[text()='Yes'][1]").click()
            else:
                page.locator("//label[text()='Process the element only once in each payroll period?']//following::label[text()='No'][1]").click()

            ### Selecting Can a person have more than one entry of this element in a payroll period?
            if datadictvalue["C_MORE_THAN_ONE_ENTRY"] == 'Yes':
                page.locator("//label[text()='Can a person have more than one entry of this element in a payroll period?']//following::label[text()='Yes'][1]").click()
            else:
                page.locator("//label[text()='Can a person have more than one entry of this element in a payroll period?']//following::label[text()='No'][1]").click()

            ## Clicking on Next button
            page.get_by_role("button", name="Next").click()
            page.wait_for_timeout(3000)

            # Calculation Rules
            ### Based on Fixed amount deductions
            if datadictvalue["C_CLCLTN_RULE"] == 'Fixed amount deduction':
                page.get_by_text("Fixed amount deduction", exact=True).click()

                # Special Rules
                ### Is this element subject to proration?
                if datadictvalue["C_ELMNT_PRRTN"] != 'N/A':
                    if datadictvalue["C_ELMNT_PRRTN"] == 'No':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='No'][1]").click()
                    elif datadictvalue["C_ELMNT_PRRTN"] == 'Yes':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='Yes'][1]").click()
                        if datadictvalue["C_PRRTN_GROUP"] != 'N/A':
                            page.wait_for_timeout(3000)
                            page.get_by_role("combobox", name="Proration Group").click()
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_GROUP"]).click()

                #### Is this element subject to retroactive changes?
                if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] != 'N/A':
                    if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'No':
                        page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()
                    elif datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                        page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                        if datadictvalue["C_RETRO_GROUP"] != 'N/A':
                            page.wait_for_timeout(2000)
                            page.get_by_role("combobox", name="Retro Group").click()
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()

                #### Do you want to stop processing when the total owed is reached? If you enable total owed, a reference is required for each deduction entry.
                if datadictvalue["C_STOP_PRCSSNG"] != 'N/A':
                    if datadictvalue["C_STOP_PRCSSNG"] == 'No':
                        page.locator("//label[text()='Do you want to stop processing when the total owed is reached? If you enable total owed, a reference is required for each deduction entry.']//following::label[text()='No'][1]").click()
                    elif datadictvalue["C_STOP_PRCSSNG"] == 'Yes':
                        page.locator("//label[text()='Do you want to stop processing when the total owed is reached? If you enable total owed, a reference is required for each deduction entry.']//following::label[text()='Yes'][1]").click()

            ### Based on Percentage deduction
            if datadictvalue["C_CLCLTN_RULE"] == 'Percentage deduction':
                page.get_by_text("Percentage deduction", exact=True).click()

                # Special Rules
                ### Is this element subject to proration?
                if datadictvalue["C_ELMNT_PRRTN"] != 'N/A':
                    if datadictvalue["C_ELMNT_PRRTN"] == 'No':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='No'][1]").click()
                    elif datadictvalue["C_ELMNT_PRRTN"] == 'Yes':
                        page.locator("//label[text()='Is this element subject to proration?']//following::label[text()='Yes'][1]").click()
                        if datadictvalue["C_PRRTN_GROUP"] != 'N/A':
                            page.wait_for_timeout(3000)
                            page.get_by_role("combobox", name="Proration Group").click()
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_PRRTN_GROUP"]).click()

                #### Is this element subject to retroactive changes?
                if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] != 'N/A':
                    if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'No':
                        page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()
                    elif datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                        page.locator("//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                        if datadictvalue["C_RETRO_GROUP"] != 'N/A':
                            page.wait_for_timeout(2000)
                            page.get_by_role("combobox", name="Retro Group").click()
                            page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_RETRO_GROUP"]).click()

                #### Do you want to stop processing when the total owed is reached? If you enable total owed, a reference is required for each deduction entry.
                if datadictvalue["C_STOP_PRCSSNG"] != 'N/A':
                    if datadictvalue["C_STOP_PRCSSNG"] == 'No':
                        page.locator("//label[text()='Do you want to stop processing when the total owed is reached? If you enable total owed, a reference is required for each deduction entry.']//following::label[text()='No'][1]").click()
                    elif datadictvalue["C_STOP_PRCSSNG"] == 'Yes':
                        page.locator("//label[text()='Do you want to stop processing when the total owed is reached? If you enable total owed, a reference is required for each deduction entry.']//following::label[text()='Yes'][1]").click()

        # Secondary Classification as Benefits After Tax
        if datadictvalue["C_SCNDRY_CLSSFCTN"] == 'Loans':
                    page.get_by_role("combobox", name="Secondary Classification").click()
                    page.wait_for_timeout(3000)
                    page.get_by_text(datadictvalue["C_SCNDRY_CLSSFCTN"], exact=True).click()
                    page.wait_for_timeout(2000)

                    page.get_by_role("button", name="Continue").click()
                    page.wait_for_timeout(3000)

                    # Entering Basic Details
                    page.get_by_label("Name", exact=True).type(datadictvalue["C_ELMNT_NAME"])
                    page.get_by_label("Reporting Name").type(datadictvalue["C_RPRTNG_NAME"])
                    page.get_by_label("Description").type(datadictvalue["C_DSCRPTN"])
                    page.get_by_placeholder("m/d/yy").clear()
                    page.get_by_placeholder("m/d/yy").type(datadictvalue["C_EFCTV_DATE"])

                    # Selecting Currency
                    page.get_by_role("combobox", name="Input Currency").click()
                    page.wait_for_timeout(2000)
                    page.get_by_text(datadictvalue["C_INPUT_CRNCY"], exact=True).click()

                    # Selecting Duration
                    if datadictvalue["C_ATMTC_ELMNT_ELGBLTY"] == 'Yes':
                        page.locator(
                            "// label[text() = 'Should every person eligible for the element automatically receive it?'] // following::label[text() = 'Yes'][1]").click()
                    else:
                        page.locator(
                            "// label[text() = 'Should every person eligible for the element automatically receive it?'] // following::label[text() = 'No'][1]").click()

                    page.wait_for_timeout(2000)
                    page.get_by_role("combobox", name="What is the earliest entry").click()
                    page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_ERLST_ENTRY_DATE"]).click()
                    page.get_by_role("combobox", name="What is the latest entry date").click()
                    page.locator("[id=\"__af_Z_window\"]").get_by_text(datadictvalue["C_LTST_ENTRY_DATE"]).click()

                    # Standard Rules

                    ###Selecting At which employment level should this element be attached?
                    if datadictvalue["C_EMPLYMNT_LEVEL_ELMNT"] == 'Assignment Level':
                        page.get_by_text("Assignment Level", exact=True).click()
                    elif datadictvalue["C_EMPLYMNT_LEVEL_ELMNT"] == 'Payroll relationship level':
                        page.get_by_text("Payroll relationship level", exact=True).click()
                    elif datadictvalue["C_EMPLYMNT_LEVEL_ELMNT"] == 'Term Level':
                        page.get_by_text("Term Level", exact=True).click()

                    ### Does this element recur each payroll period, or does it require explicit entry?
                    if datadictvalue["C_ELMNT_RCRRNG_NNRCRRNG"] == 'Recurring':
                        page.get_by_text("Recurring", exact=True).click()
                    else:
                        page.get_by_text("Nonrecurring", exact=True).click()

                    ### What should happen when there are insufficient funds to cover the deductions?
                    if datadictvalue["C_INSFFCNT_PRTL_DDCTN"] == 'Do not take a partial deduction or create arrears':
                        page.get_by_text("Do not take a partial deduction or create arrears", exact=True).click()

                    elif datadictvalue[
                        "C_INSFFCNT_PRTL_DDCTN"] == 'Do not take partial deduction, place all in arrears':
                        page.get_by_text("Do not take partial deduction, place all in arrears", exact=True).click()

                    elif datadictvalue[
                        "C_INSFFCNT_PRTL_DDCTN"] == 'Take a partial deduction, but do not create arrears':
                        page.get_by_text("Take a partial deduction, but do not create arrears", exact=True).click()

                    elif datadictvalue[
                        "C_INSFFCNT_PRTL_DDCTN"] == 'Take a partial deduction, place remaining in arrears':
                        page.get_by_text("Take a partial deduction, place remaining in arrears", exact=True).click()

                    ### Selecting Process the element only once in each payroll period?
                    if datadictvalue["C_PRCSS_ELMNT_ONLY_ONCE"] == 'Yes':
                        page.locator(
                            "//label[text()='Process the element only once in each payroll period?']//following::label[text()='Yes'][1]").click()
                    else:
                        page.locator(
                            "//label[text()='Process the element only once in each payroll period?']//following::label[text()='No'][1]").click()

                    ### Selecting Can a person have more than one entry of this element in a payroll period?
                    if datadictvalue["C_MORE_THAN_ONE_ENTRY"] == 'Yes':
                        page.locator(
                            "//label[text()='Can a person have more than one entry of this element in a payroll period?']//following::label[text()='Yes'][1]").click()
                    else:
                        page.locator(
                            "//label[text()='Can a person have more than one entry of this element in a payroll period?']//following::label[text()='No'][1]").click()

                    ## Clicking on Next button
                    page.get_by_role("button", name="Next").click()
                    page.wait_for_timeout(3000)

                    # Calculation Rules
                    ### Based on Fixed amount deductions
                    if datadictvalue["C_CLCLTN_RULE"] == 'Fixed amount deduction':
                        page.get_by_text("Fixed amount deduction", exact=True).click()

                        # Special Rules
                        ### Is this element subject to proration?
                        if datadictvalue["C_ELMNT_PRRTN"] != 'N/A':
                            if datadictvalue["C_ELMNT_PRRTN"] == 'No':
                                page.locator(
                                    "//label[text()='Is this element subject to proration?']//following::label[text()='No'][1]").click()
                            elif datadictvalue["C_ELMNT_PRRTN"] == 'Yes':
                                page.locator(
                                    "//label[text()='Is this element subject to proration?']//following::label[text()='Yes'][1]").click()
                                if datadictvalue["C_PRRTN_GROUP"] != 'N/A':
                                    page.wait_for_timeout(3000)
                                    page.get_by_role("combobox", name="Proration Group").click()
                                    page.locator("[id=\"__af_Z_window\"]").get_by_text(
                                        datadictvalue["C_PRRTN_GROUP"]).click()

                        #### Is this element subject to retroactive changes?
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] != 'N/A':
                            if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'No':
                                page.locator(
                                    "//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()
                            elif datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                                page.locator(
                                    "//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                                if datadictvalue["C_RETRO_GROUP"] != 'N/A':
                                    page.wait_for_timeout(2000)
                                    page.get_by_role("combobox", name="Retro Group").click()
                                    page.locator("[id=\"__af_Z_window\"]").get_by_text(
                                        datadictvalue["C_RETRO_GROUP"]).click()

                        #### Do you want to stop processing when the total owed is reached? If you enable total owed, a reference is required for each deduction entry.
                        if datadictvalue["C_STOP_PRCSSNG"] != 'N/A':
                            if datadictvalue["C_STOP_PRCSSNG"] == 'No':
                                page.locator(
                                    "//label[text()='Do you want to stop processing when the total owed is reached? If you enable total owed, a reference is required for each deduction entry.']//following::label[text()='No'][1]").click()
                            elif datadictvalue["C_STOP_PRCSSNG"] == 'Yes':
                                page.locator(
                                    "//label[text()='Do you want to stop processing when the total owed is reached? If you enable total owed, a reference is required for each deduction entry.']//following::label[text()='Yes'][1]").click()

                    ### Based on Percentage deduction
                    if datadictvalue["C_CLCLTN_RULE"] == 'Percentage deduction':
                        page.get_by_text("Percentage deduction", exact=True).click()

                        # Special Rules
                        ### Is this element subject to proration?
                        if datadictvalue["C_ELMNT_PRRTN"] != 'N/A':
                            if datadictvalue["C_ELMNT_PRRTN"] == 'No':
                                page.locator(
                                    "//label[text()='Is this element subject to proration?']//following::label[text()='No'][1]").click()
                            elif datadictvalue["C_ELMNT_PRRTN"] == 'Yes':
                                page.locator(
                                    "//label[text()='Is this element subject to proration?']//following::label[text()='Yes'][1]").click()
                                if datadictvalue["C_PRRTN_GROUP"] != 'N/A':
                                    page.wait_for_timeout(3000)
                                    page.get_by_role("combobox", name="Proration Group").click()
                                    page.locator("[id=\"__af_Z_window\"]").get_by_text(
                                        datadictvalue["C_PRRTN_GROUP"]).click()

                        #### Is this element subject to retroactive changes?
                        if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] != 'N/A':
                            if datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'No':
                                page.locator(
                                    "//label[text()='Is this element subject to retroactive changes?']//following::label[text()='No'][1]").click()
                            elif datadictvalue["C_ELMNT_RTRCTV_CHNGS"] == 'Yes':
                                page.locator(
                                    "//label[text()='Is this element subject to retroactive changes?']//following::label[text()='Yes'][1]").click()
                                if datadictvalue["C_RETRO_GROUP"] != 'N/A':
                                    page.wait_for_timeout(2000)
                                    page.get_by_role("combobox", name="Retro Group").click()
                                    page.locator("[id=\"__af_Z_window\"]").get_by_text(
                                        datadictvalue["C_RETRO_GROUP"]).click()

                        #### Do you want to stop processing when the total owed is reached? If you enable total owed, a reference is required for each deduction entry.
                        if datadictvalue["C_STOP_PRCSSNG"] != 'N/A':
                            if datadictvalue["C_STOP_PRCSSNG"] == 'No':
                                page.locator(
                                    "//label[text()='Do you want to stop processing when the total owed is reached? If you enable total owed, a reference is required for each deduction entry.']//following::label[text()='No'][1]").click()
                            elif datadictvalue["C_STOP_PRCSSNG"] == 'Yes':
                                page.locator(
                                    "//label[text()='Do you want to stop processing when the total owed is reached? If you enable total owed, a reference is required for each deduction entry.']//following::label[text()='Yes'][1]").click()

        # Moving to Next Page
        page.get_by_role("button", name="Next").click()
        page.wait_for_timeout(3000)
        # Saving the Record
        page.get_by_role("button", name="Submit").click()
        page.wait_for_timeout(30000)
        page.locator("//span[text()='K']").click()
        page.wait_for_timeout(20000)
        if page.locator("//span[text()='K']").is_visible():
            page.locator("//span[text()='K']").click()
            page.wait_for_timeout(10000)
        try:
            expect(page.locator("//h1[text()='Elements']")).to_be_visible()
            page.wait_for_timeout(3000)
            print("Element Entry Created Successfully")
            datadictvalue["RowStatus"] = "Element Saved"
        except Exception as e:
            print("Unable to Create the Element Entry")
            datadictvalue["RowStatus"] = "Unable to Create the Element Entry"

        i = i + 1

    OraSignOut(page, context, browser, videodir)
    return datadict

# ****** Execution Starts Here ******
print("Process Started At - ", datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
if CheckWrkbkForProcessing(SOURCE_DIR_PATH + PAYROLL_DEDUCTIONS_WRKBK, VOLUNTRY_DEDUCTIONS):
    CreateWrkbkForProcessing(SOURCE_DIR_PATH + PAYROLL_DEDUCTIONS_WRKBK, VOLUNTRY_DEDUCTIONS,PRCS_DIR_PATH + PAYROLL_DEDUCTIONS_WRKBK)
    rows, cols, datadictwrkbk = ImportWrkbk(PRCS_DIR_PATH + PAYROLL_DEDUCTIONS_WRKBK, VOLUNTRY_DEDUCTIONS)
    if rows > 0:
        with sync_playwright() as pw:
            output = configure(pw, rows, datadictwrkbk,VIDEO_DIR_PATH + re.split(".xlsx", PAYROLL_DEDUCTIONS_WRKBK)[0] + "_" + VOLUNTRY_DEDUCTIONS)
        write_status(output, RESULTS_DIR_PATH + re.split(".xlsx", PAYROLL_DEDUCTIONS_WRKBK)[0] + "_" + VOLUNTRY_DEDUCTIONS + "_Results_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".xlsx")
    else:
        print("No data rows to process. Check the source workbook to ensure it is valid!")
print("Process Ended At - ", datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

